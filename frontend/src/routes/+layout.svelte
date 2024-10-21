<script>
	import '../app.css';
</script>

<style lang="postcss">
	:global(html) {
		@apply bg-black text-white text-xl;
		caret-color: white;
	}
</style>

<div class="flex h-dvh flex-col overflow-auto overscroll-contain">
	<slot />
</div>
