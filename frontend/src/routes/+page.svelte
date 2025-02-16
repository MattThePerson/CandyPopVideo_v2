<script>
    console.log("Hey monkeyboy");

    fetch('/api/hello')
        .then(res => {
            console.log(res);
            return res.json()
        }).then(data => {
            console.log(data);
        }).catch(err => {
            console.error(err);
        })
</script>

<h1>Welcome to the Home Page</h1>
