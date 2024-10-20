<script lang="ts">
	import { onMount } from 'svelte';
	import { MessageType, type ConsoleMessage, Origin } from '$lib/console_text';

	let input = '';
	let history: ConsoleMessage[] = [{ type: MessageType.Code, origin: Origin.System, content: '                               __\n   ____ ___  ____  _________  / /_\n  / __ `__ \\/ __ \\/ ___/ __ \\/ __ \\\n / / / / / / /_/ / /  / /_/ / / / /\n/_/ /_/ /_/\\____/_/  / .___/_/ /_/\n                    /_/' }];
	let inputElement: HTMLInputElement;

	function handle_input_keydown(event: KeyboardEvent) {
		if (event.key !== 'Enter') return;
		console.log(input);
		history = [...history, { type: MessageType.Text, origin: Origin.User, content: input }];
		input = '';
	}

	onMount(() => {
		inputElement.focus();
	});
</script>

<div class="flex h-full flex-row gap-5 p-5">
	<div class="h-full w-3/4 border-2 border-white pl-5">
		{#each history as entry}
			{#if entry.type === MessageType.Code}
				<pre>{entry.content}</pre>
			{:else if entry.origin === Origin.System}
				<p class="text-gray-400">{entry.content}</p>
			{:else}
				<div class="flex flex-row text-gray-400">
                    <pre>>> </pre>
                    <p>{entry.content}</p>
                </div>
			{/if}
		{/each}
		<div class="flex flex-row">
			<pre>>> </pre>
			<input bind:this={inputElement} bind:value={input} on:keydown={handle_input_keydown} class="resize-none bg-black text-white focus:outline-none" placeholder="" />
		</div>
	</div>
	<div class="h-full w-1/4 border-2 border-white"></div>
</div>
