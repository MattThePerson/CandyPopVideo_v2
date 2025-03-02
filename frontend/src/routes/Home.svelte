<script>
    import { onMount } from "svelte";

    console.log("Hey monkeyboy");

    onMount(() => {
        fetch('/api/hello')
        .then(res => {
            console.log(res);
            return res.json()
        }).then(data => {
            console.log(data);
        }).catch(err => {
            console.error(err);
        })
    });
    </script>

<h1>Welcome to the Home Page CHANGES</h1>
