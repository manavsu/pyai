<script lang="ts">
	import { onMount, afterUpdate } from 'svelte';
	import { MessageType, type ConsoleMessage, Origin, NotificationType, type Notification } from '$lib/console_text';
	import { create_new_agent, query_agent, get_file as get_file_url } from '$lib/agent';
	import { marked } from 'marked';
	import { getFileType, replaceSandboxCall } from '$lib/utils';
	import Loader from '$lib/loader.svelte';

	let input = '';
	let history: ConsoleMessage[] = [
		{ type:MessageType.Code, origin:Origin.System, content:"                       _\n    ____  __  ______ _(_)\n   / __ \/ / / / __ `/ /\n  / /_/ / /_/ / /_/ / /\n / .___/\__, /\__,_/_/\n/_/    /____/"},
		// { type: MessageType.Code, origin: Origin.System, content: '                               __\n   ____ ___  ____  _________  / /_\n  / __ `__ \\/ __ \\/ ___/ __ \\/ __ \\\n / / / / / / /_/ / /  / /_/ / / / /\n/_/ /_/ /_/\\____/_/  / .___/_/ /_/\n                    /_/' },
		{ type: MessageType.Code, origin: Origin.System, content: 'Agent: gpt-4o-mini\nTools: [Juypter Notebook]'},
	];
	let input_element: HTMLInputElement;
	let file_to_url: { [key: string]: string } = {};
	let attached_files: string[] = [];
	let loading = false;
	let chatEnd:any;

	async function handle_input_keydown(event: KeyboardEvent) {
		if (event.key !== 'Enter') return;
		await submit_and_query();
	}

	async function submit_and_query() {
		loading = true;
		history = [...history, { type: MessageType.Text, origin: Origin.User, content: input, attachments: attached_files }];
		history = [...history, { type: MessageType.Loading, origin: Origin.System, content: '' }];
		let query_attachments = attached_files.map(u => ({ file: file_to_url[u], url: u }));
		attached_files = [];
		const user_input = input;
		input = '';
		let response = await query_agent(user_input, query_attachments);

		await handle_notifications(response?.notifications);
		history.pop();
		history = [...history, { type: MessageType.Markdown, origin: Origin.Agent, content: response?.message}];
		loading = false;
		input_element.focus();
	}

	async function handle_notifications(notifications: Notification[]) {
		if (!notifications) return;
		console.log(notifications);

		for (const notification of notifications) {
			if (notification.type == NotificationType.File) {
				console.log(notification.type);
				let url = await get_file_url(notification.content);
				if (url) {
					const file_type = getFileType(notification.content);
					history = [...history, { type: file_type, origin: Origin.Agent, content: url! }];
					file_to_url[url!] = notification.content;
					console.log(notification, file_type);
				}
			}
		}
	}

	function handle_file_input(event: Event) {
		const input = event.target as HTMLInputElement;
		if (!input.files?.length) return;
		for (const file of input.files) {
			const url = URL.createObjectURL(file);
			file_to_url[url] = file.name;
			console.log(file.name, url);
			attached_files = [...attached_files, url!];
		}
		input_element.focus();
	}

	function remove_attached_file(url: string) {
		attached_files = attached_files.filter((file) => file !== url);
	}

	onMount(() => {
		input_element.focus();
		create_new_agent();
	});

	afterUpdate(() => {
        chatEnd.scrollIntoView({ behavior: 'smooth' });
    });
</script>

<div class="flex h-full flex-row gap-5 p-5">
	<div class="mx-auto flex h-full w-5/6 flex-col gap-5 pl-5 md:w-3/4 lg:w-3/5 xl:w-1/2 pb-10">
		<div class="flex flex-col w-full flex-grow gap-2 overflow-auto overscroll-contain">
			{#each history as entry}
				{#if entry.type === MessageType.Code}
					<pre>{entry.content}</pre>
				{:else if entry.origin === Origin.System}
					{#if entry.type === MessageType.Loading}
						<Loader />
					{:else}
						<p class="text-gray-400">{entry.content}</p>
					{/if}
				{:else if entry.origin === Origin.User}
					<div class="flex flex-row gap-2 text-gray-400">
						{#if entry.attachments}
							{#each entry.attachments as url}
								<a href={url} target="_blank" class="text-gray-400">[{file_to_url[url]}]</a>
							{/each}
						{/if}
						<p>></p>
						<p>{entry.content}</p>
					</div>
				{:else if entry.origin === Origin.Agent}
					<div class="mx-auto w-5/6">
						{#if entry.type === MessageType.Text}
							<p>{entry.content}</p>
						{:else if entry.type === MessageType.Markdown}
							<div class="markdown">
								{@html marked(entry.content)}
							</div>
						{:else if entry.type === MessageType.File}
							<a href={entry.content} download={file_to_url[entry.content]} class="text-blue-500">[{file_to_url[entry.content]}]</a>
						{:else if entry.type === MessageType.Image}
							<img class="p-2" src={entry.content} alt={file_to_url[entry.content]} aria-hidden="true" />
						{:else if entry.type === MessageType.TextFile}
							{#await fetch(entry.content).then((res) => res.text()) then fileContent}
								<pre>{fileContent.split('\n').slice(0, 5).join('\n')}</pre>
							{/await}
						{/if}
					</div>
				{/if}
			{/each}
			<div bind:this={chatEnd}></div>
		</div>
		<div class="flex w-7/8 flex-row gap-2">
			<input type="file" disabled={loading} id="fileInputElement" on:change={handle_file_input} class="hidden" />
			<label for="fileInputElement" class="{loading ? "text-gray-400" : "text-blue-500 hover:scale-110" } duration-400 cursor-pointer transition ">[Attach File]</label>
			{#each attached_files as url}
				<button on:click={() => remove_attached_file(url)} class="duration-400 text-gray-400 transition hover:scale-90">[{file_to_url[url]}]</button>
			{/each}
			<p>></p>
			<input bind:this={input_element} bind:value={input} on:keydown={handle_input_keydown} disabled={loading} class="flex-grow px-3 rounded-md resize-none bg-black {loading ? "" : "hover:bg-gray-800"} text-white transition duration-400 focus:outline-none" placeholder="" />
			<button on:click={submit_and_query} class="duration-400 pr-2 transition {loading || !input? "text-gray-400" : "hover:scale-110"}" disabled={loading || !input}>[Submit]</button>
		</div>
	</div>
	<!-- <div class="h-full w-1/4 border-2 border-white"></div> -->
</div>
