<script>
    import Button from "$lib/components/ui/button/button.svelte";

    import { onMount } from "svelte";

    console.log("Hey monkeyboy");

    onMount(() => {
        fetch("/api/hello")
            .then((res) => {
                console.log(res);
                return res.json();
            })
            .then((data) => {
                console.log(data);
            })
            .catch((err) => {
                console.error(err);
            });
    });
</script>

<h1 class="text-3xl font-bold underline">
    Welcome to the Home Page with Tailwind!
</h1>
<Button>this is a fookin button!</Button>


