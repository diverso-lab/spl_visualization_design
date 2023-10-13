window.addEventListener('DOMContentLoaded', (event) => {
    loadImagesFromFolder('graphs');
    loadImagesFromFolder('tables');
});

function loadImagesFromFolder(folderName) {
    // Assume you have up to 20 images in each folder. Adjust as needed.
    for (let i = 1; i <= 20; i++) {
        let img = new Image();
        img.src = `${folderName}/image${i}.png`;

        img.onload = function() {
            document.getElementById(folderName).appendChild(img);
        };
    }
}