
    <script>
        document.getElementById('toggleMusic').addEventListener('click', function() {
            var music = document.getElementById('backgroundMusic');
            if (music.paused) {
                music.play();
                this.innerText = "Pause Music";
            } else {
                music.pause();
                this.innerText = "Play Music";
            }
        });
    </script>
