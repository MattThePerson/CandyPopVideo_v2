


/* MAIN */

let related_videos_load_amount = 24;
let related_videos_loaded = 0;



makeApiRequestGET('api/get/random-spotlight-video', [], (arg) => {
    
    console.log(arg);
    makeApiRequestGET('api/get-video-data', [arg.hash], (videodata) => {
        
        let date = Date().split(' ').slice(0,4).join(' ');
        document.querySelector('.top-container h2').innerText += ' ' + date;
        
        makeApiRequestGET('api/query/get-similar-videos', [videodata.hash, 0, related_videos_load_amount], search_results => {
            generate_results(search_results);
        });
        related_videos_loaded += related_videos_load_amount;
    
        // expand related results button
        document.getElementById('expand-results-button').addEventListener('click', arg => {
            console.log('Loading more related videos. Getting from index: ' + related_videos_loaded);
            makeApiRequestGET('api/query/get-similar-videos', [videodata.hash, related_videos_loaded, related_videos_load_amount], search_results => {
                generate_results(search_results);
            });
            related_videos_loaded += related_videos_load_amount;
        });
    });
})