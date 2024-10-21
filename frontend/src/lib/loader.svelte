<script lang="ts">
    import { onDestroy, onMount } from 'svelte';

    let current = "";
    const cycle = ["|", "/", "-", "\\"];

    function update() {
        current = cycle[(cycle.indexOf(current) + 1) % cycle.length];
    }

    onMount(() => {
		setInterval(() => {
            update();
        }, 200);
	});
</script>

<p class="text-2xl">{current}</p>