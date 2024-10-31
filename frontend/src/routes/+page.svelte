<script lang="ts">
	import { onMount, afterUpdate } from 'svelte';
	import { MessageType, type ConsoleMessage, Origin, NotificationType, type Notification } from '$lib/console_text';
	import { create_new_agent, query_agent, get_file as get_file_url } from '$lib/agent';
	import { marked } from 'marked';
	import { getFileType, replaceSandboxCall } from '$lib/utils';
	import Loader from '$lib/loader.svelte';

	const logo = '                       _\n    ____  __  ______ _(_)\n   / __ \\/ / / / __ `/ /\n  / /_/ / /_/ / /_/ / /\n / .___/__,  /_,_/_/_/\n/_/    /____/';
	let input = '';
	let history: ConsoleMessage[] = [
		{ type: MessageType.Logo, origin: Origin.System, content: logo },
		// { type: MessageType.Code, origin: Origin.System, content: '                               __\n   ____ ___  ____  _________  / /_\n  / __ `__ \\/ __ \\/ ___/ __ \\/ __ \\\n / / / / / / /_/ / /  / /_/ / / / /\n/_/ /_/ /_/\\____/_/  / .___/_/ /_/\n                    /_/' },
		{ type: MessageType.Text, origin: Origin.System, content: 'Agent: gpt-4o-mini\nTools: [Jupyter Notebook]' }
	];
	let input_element: HTMLInputElement;
	let file_to_url: { [key: string]: string } = {};
	let attached_files: string[] = [];
	let loading = false;
	let chatEnd: any;
	let code_url: string | null = null;
	let agent_id: string | null = null;

	async function handle_input_keydown(event: KeyboardEvent) {
		if (event.key !== 'Enter') return;
		await submit_and_query();
	}

	async function submit_and_query() {
		loading = true;
		history = [...history, { type: MessageType.Text, origin: Origin.User, content: input, attachments: attached_files }];
		history = [...history, { type: MessageType.Loading, origin: Origin.System, content: '' }];
		let query_attachments = attached_files.map((u) => ({ file: file_to_url[u], url: u }));
		attached_files = [];
		const user_input = input;
		input = '';
		let response = await query_agent(agent_id!, user_input, query_attachments);

		await handle_notifications(response?.notifications);
		history = history.filter((entry) => entry.type != MessageType.Loading);
		code_url = await get_file_url(agent_id!, 'notebook.ipynb');
		history = [...history, { type: MessageType.Markdown, origin: Origin.Agent, content: response?.message }];
		loading = false;
		input_element.focus();
	}

	async function handle_notifications(notifications: Notification[]) {
		if (!notifications) return;
		console.log(notifications);

		for (const notification of notifications) {
			if (notification.type == NotificationType.File) {
				console.log(notification.type);
				let url = await get_file_url(agent_id!, notification.content);
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

	onMount(async () => {
		input_element.focus();
		loading = true;
		agent_id = await create_new_agent();
		loading = false;
	});

	afterUpdate(() => {
		chatEnd.scrollIntoView({ behavior: 'smooth' });
	});
</script>

<div class="flex flex-row items-center justify-between p-5 px-5">
	<pre class="text-3xl leading-none">pyai</pre>
	<div class="flex flex-row text-xl sm:text-3xl">
		<a href={code_url} download="notebook.ipynb" class="{loading || !code_url ? 'text-gray-600' : ' hover:scale-110'} mine-w-10 duration-400 cursor-pointer text-nowrap pb-2 transition" title="Download code"><pre>[&lt;/&gt;]</pre></a>
	</div>
</div>
<hr class="mx-5 border-gray-600" />
<div class="md:w-5/7 mx-auto flex h-full w-full flex-col gap-5 px-10 pb-10 lg:w-3/5 xl:w-2/3">
	<div class="flex w-full flex-grow flex-col gap-2 overflow-auto overscroll-contain">
		{#each history as entry}
			{#if entry.type === MessageType.Code}
				<pre>{entry.content}</pre>
			{:else if entry.origin === Origin.System}
				{#if entry.type === MessageType.Loading}
					<Loader />
				{:else if entry.type === MessageType.Text}
					<pre class="text-gray-400">{entry.content}</pre>
				{:else if entry.type === MessageType.Logo}
					<pre class="leading-none text-gray-400">{entry.content}</pre>
				{/if}
			{:else if entry.origin === Origin.User}
				<div class="flex flex-row gap-2 text-gray-400">
					{#if entry.attachments}
						{#each entry.attachments as url}
							<a href={'http://' + url} target="_blank" class="duration-400 text-gray-400 transition hover:scale-110">[{file_to_url[url]}]</a>
						{/each}
					{/if}
					<p>></p>
					<p>{entry.content}</p>
				</div>
			{:else if entry.origin === Origin.Agent}
				<div class="xs:max-w-full sm:max-w-5/6 w-fit justify-self-center">
					{#if entry.type === MessageType.Text}
						<p>{entry.content}</p>
					{:else if entry.type === MessageType.Markdown}
						<div class="markdown">
							{@html marked(entry.content)}
						</div>
					{:else if entry.type === MessageType.File}
						<a href={entry.content} download={file_to_url[entry.content]} class="duration-400 w-fit text-blue-500 transition hover:scale-110">[{file_to_url[entry.content]}]</a>
					{:else if entry.type === MessageType.Image}
						<a href={entry.content} download={file_to_url[entry.content]} class="duration-400 w-fit text-blue-500 transition hover:scale-110">[{file_to_url[entry.content]}]</a>
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
	<div class="flex flex-col gap-2">
		<div class="flex flex-row flex-wrap gap-2">
			{#each attached_files as url}
				<button on:click={() => remove_attached_file(url)} class="duration-400 text-nowrap pb-2 text-gray-600 transition hover:scale-90">[{file_to_url[url]}]</button>
			{/each}
		</div>
		<div class="flex flex-row gap-2">
			<p class="text-3xl {loading ? 'text-gray-600' : ''}">></p>
			<input bind:this={input_element} bind:value={input} on:keydown={handle_input_keydown} disabled={loading} class="flex-grow border-b bg-black px-3 pb-2 {loading ? 'border-gray-600' : ''}  duration-400 text-white transition focus:outline-none" placeholder="" />
			<button on:click={submit_and_query} class="duration-400 pb-2 transition {loading || !input ? 'text-gray-600' : 'hover:scale-110'} text-xl sm:text-3xl" disabled={loading || !input} title="Submit"><pre>[↵]</pre></button>
			<input type="file" disabled={loading} id="fileInputElement" on:change={handle_file_input} class="hidden min-w-10" />
			<label for="fileInputElement" class="{loading ? 'text-gray-600' : ' hover:scale-110'} mine-w-10 duration-400 cursor-pointer text-nowrap pb-2 text-xl sm:text-3xl transition" title="Attach file"><pre>[+]</pre></label>
		</div>
	</div>
	<div class="flex flex-row justify-around gap-5">
		<div class="flex flex-row gap-5">
			<!-- <button class="" -->
		</div>
	</div>
</div>
