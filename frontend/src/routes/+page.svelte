<script lang="ts">
	import { onMount } from 'svelte';
	import { MessageType, type ConsoleMessage, Origin, NotificationType, type Notification } from '$lib/console_text';
	import { create_new_agent, query_agent, get_file } from '$lib/agent';
	import { marked } from 'marked';

	let input = '';
	let history: ConsoleMessage[] = [{ type: MessageType.Code, origin: Origin.System, content: '                               __\n   ____ ___  ____  _________  / /_\n  / __ `__ \\/ __ \\/ ___/ __ \\/ __ \\\n / / / / / / /_/ / /  / /_/ / / / /\n/_/ /_/ /_/\\____/_/  / .___/_/ /_/\n                    /_/' }];
	let inputElement: HTMLInputElement;

	async function handle_input_keydown(event: KeyboardEvent) {
		if (event.key !== 'Enter') return;
		console.log(input);
		history = [...history, { type: MessageType.Text, origin: Origin.User, content: input }];
		const user_input = input;
		input = '';
		let response = await query_agent(user_input);

		await handle_notifications(response?.notifications);

		history = [...history, { type: MessageType.Markdown, origin: Origin.Agent, content: response?.message }];

		inputElement.focus();
	}

	async function handle_notifications(notifications: Notification[]) {
		if (!notifications) return;
		for (const notification of notifications) {
			if (notification.type === NotificationType.File) {
				let file = await get_file(notification.content);
				history = [...history, { type: MessageType.File, origin: Origin.Agent, content: file! }];
			}
			console.log(notification);
		}
	}

	onMount(() => {
		inputElement.focus();
		create_new_agent();
	});
</script>

<div class="flex h-full flex-row gap-5 p-5">
	<div class="h-full w-full overflow-auto overscroll-contain border-2 border-white pl-5">
		{#each history as entry}
			{#if entry.type === MessageType.Code}
				<pre>{entry.content}</pre>
			{:else if entry.origin === Origin.System}
				<p class="text-gray-400">{entry.content}</p>
			{:else if entry.origin === Origin.User}
				<div class="flex flex-row text-gray-400">
					<pre>>> </pre>
					<p>{entry.content}</p>
				</div>
			{:else if entry.origin === Origin.Agent}
				{#if entry.type === MessageType.Text}
					<p>{entry.content}</p>
				{:else if entry.type === MessageType.Markdown}
					<div class="markdown">
						{@html marked(entry.content)}
					</div>
				{/if}
			{/if}
		{/each}
		<div class="flex flex-row">
			<pre>>> </pre>
			<input bind:this={inputElement} bind:value={input} on:keydown={handle_input_keydown} class="w-full resize-none bg-black text-white focus:outline-none" placeholder="" />
		</div>
	</div>
	<!-- <div class="h-full w-1/4 border-2 border-white"></div> -->
</div>
