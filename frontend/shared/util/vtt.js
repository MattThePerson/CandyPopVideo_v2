

export function configure_teaser_thumb_spritesheet(spritesheet_src, thumbnail_container, parent_container) {
    
    const vtt_src = spritesheet_src.replace('.jpg', '.vtt');
    
    // First, load and parse the VTT file to get the sprite information
    fetch(vtt_src)
        .then(response => response.text())
        .then(vttText => {
            console.log('got vtt text');

            // Parse the VTT file to extract sprite coordinates
            const sprites = parseVTT(vttText);
            if (sprites.length === 0) {
                throw new Error('No sprites parsed from vtt file:', vtt_src);
            };
            
            // Set up the spritesheet as the background for the thumbnail container
            thumbnail_container.style.backgroundImage = `url("${spritesheet_src}")`;
            thumbnail_container.style.backgroundRepeat = 'no-repeat';
            
            // load image to get spritesheet height
            const img = new Image();
            img.src = spritesheet_src;

            img.onload = () => {
                const thumbAspectRatio = sprites[0].w / sprites[0].h;
                const thumbContainerHeight = parent_container.clientHeight; // parents height because of possible display: none;
                thumbnail_container.style.width = (thumbAspectRatio * thumbContainerHeight) + 'px';

                // determine background image scale factor
                const scaleFactor = (thumbContainerHeight / sprites[0].h);
                thumbnail_container.style.backgroundSize = (img.naturalWidth * scaleFactor) + 'px ' + (img.naturalHeight * scaleFactor) + 'px';

                // Calculate how many thumbnails we have
                const thumbCount = sprites.length;
                
                // Handle mouse movement to update the thumbnail
                parent_container.addEventListener('mousemove', (e) => {
                    // Calculate the percentage of mouse position within the parent container
                    const rect = parent_container.getBoundingClientRect();
                    const xPos = e.clientX - rect.left;

                    const perc = Math.max(0, Math.min(1, xPos / rect.width));
                    const thumbIndex = Math.floor(perc * (thumbCount));
                    
                    const sprite = sprites[thumbIndex];
                    thumbnail_container.style.backgroundPosition = `-${sprite.x*scaleFactor}px -${sprite.y*scaleFactor}px`;
                });
                
            }
        })
        .catch(error => {
            console.error('Error loading thumbnails:', error);
        });
}

// Helper function to parse VTT files containing sprite metadata
function parseVTT(vttText) {
    const sprites = [];
    const lines = vttText.split('\n');
    
    // The VTT format we're expecting has entries like:
    // 00:00:00.000 --> 00:00:00.000
    // xywh=0,0,160,90
    
    for (let i = 0; i < lines.length; i++) {
        if (lines[i].includes('xywh=')) {
            const coords = lines[i].split('xywh=')[1].split(',');
            if (coords.length === 4) {
                sprites.push({
                    x: parseInt(coords[0]),
                    y: parseInt(coords[1]),
                    w: parseInt(coords[2]),
                    h: parseInt(coords[3])
                });
            }
        }
    }
    
    return sprites;
}