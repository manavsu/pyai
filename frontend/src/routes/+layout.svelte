<script>
	import '$lib/app.css';
</script>

<style lang="postcss">
	:global(html) {
		@apply bg-black text-white;
		caret-color: white;
	}
</style>

<div class="flex h-dvh flex-col overflow-auto overscroll-contain sm:text-xl">
	<slot />
</div>
