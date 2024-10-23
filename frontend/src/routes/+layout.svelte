<script>
	import '$lib/app.css';

	const logo = '                       _\n    ____  __  ______ _(_)\n   / __ \\/ / / / __ `/ /\n  / /_/ / /_/ / /_/ / /\n / .___/__, /__,_/_/_/\n/_/    /____/';
</script>

<style lang="postcss">
	:global(html) {
		@apply bg-black text-white;
		caret-color: white;
	}
</style>


<div class="flex h-dvh w-dvw flex-col overflow-auto overscroll-contain sm:text-xl">
	<slot />
</div>
