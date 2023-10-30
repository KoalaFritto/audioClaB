document.addEventListener('DOMContentLoaded', function() {
    const simpleBarInstance = new SimpleBar(document.querySelector('.playlist-container'));
 });
 
function getPlaylistVideos(playlistId, apiKey, callback) {
    var apiUrl = `https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId=${playlistId}&key=${apiKey}`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            var videos = data.items.filter(item => {
                return item.snippet.title !== "Private video" && item.snippet.status.privacyStatus !== "private";
            }).map(item => item.snippet.resourceId.videoId);
            callback(videos);
        })
        .catch(error => console.error('Errore nel recupero dei video:', error));
}

// Funzione per inizializzare il player con la lista dei video
function initPlayer(playlistVideos) {
    var player = new YT.Player('player', {
        height: '480',
        width: '360',
        videoId: playlistVideos[0],
        playerVars: {
            listType: 'playlist',
            list: playlistVideos.join(','),
            controls: 1,
            showinfo: 1,
            rel: 0
        }
    });
}
// Usa la funzione per ottenere i video della playlist
getPlaylistVideos('PLZ9YASQIi96hSLc9AZA6r3ET4Qafys9U7', 'AIzaSyCRxPUUDGCZ7_kW3FS60plxDKzJPLybm2Q', function(videos) {
    initPlayer(videos);
});
// Funzione per aggiungere un nuovo evento
function aggiungiEvento(titolo, data, citta, link) {
    var containerEventi = document.getElementById("tour-events");

    // Crea un nuovo elemento per l'evento
    var nuovoEvento = document.createElement("div");
    nuovoEvento.className = "evento";

    // Costruisci l'HTML dell'evento con titolo, data, città e link
    nuovoEvento.innerHTML = `
        <h2>${titolo} - ${citta}</h2>
        <p>${data} <a href="${link}" target="_blank">(Per maggiori informazioni)</a></p>
    `;

    // Aggiungi l'evento al container
    containerEventi.appendChild(nuovoEvento);

    // Rimuove il messaggio "Non ci sono eventi in programma" se presente
    var messaggio = document.getElementById("no-events-message");
    if (messaggio) {
        containerEventi.removeChild(messaggio);
    }
}

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const player = new Plyr('#plyr-audio');
});

window.addEventListener('scroll', function() {
    const textOverlay = document.querySelector('.text-overlay');
    const scrollPosition = window.scrollY;
    const opacity = 1 - scrollPosition / 500; /* Regola il valore 500 per determinare la velocità di decrescimento */
    textOverlay.style.opacity = opacity;
});

document.addEventListener('DOMContentLoaded', function() {
    autosize(document.querySelectorAll('.autosize'));
});

document.addEventListener('DOMContentLoaded', () => {
    const audio = document.getElementById('custom-audio');
    const playPauseButton = document.getElementById('play-pause');
    const nextTrackButton = document.getElementById('next-track');
    const prevTrackButton = document.getElementById('prev-track');
    const progress = document.querySelector('.progress');
    const progressKnob = document.querySelector('.progress-knob');
    const durationDisplay = document.querySelector('.duration');
    const playlist = document.querySelectorAll('.playlist li');
    const songInfo = document.querySelector('.song-info'); 

    let isDragging = false;
    let currentTrack = 0;
    let currentSong = playlist[currentTrack].textContent; 
    
    function playTrack(index) {
        if (currentTrack === null) {
            alert('Devi selezionare prima un brano!');
            return;
        }

        audio.src = playlist[index].getAttribute('data-src');
        audio.play();
        playPauseButton.textContent = 'Pause';
        currentSong = playlist[index].textContent; 
        updateSongInfo(); 
    }

    function updateSongInfo() {
        songInfo.textContent = currentSong;
    }

    function updateProgressBar() {
        const progressPercentage = (audio.currentTime / audio.duration) * 100;
        progress.style.width = `${progressPercentage}%`;

        const knobPosition = (progressPercentage / 100) * (progress.offsetWidth - progressKnob.offsetWidth);
        progressKnob.style.left = `${knobPosition}px`;

        const remainingTime = audio.duration - audio.currentTime;
        const minutes = Math.floor(remainingTime / 60);
        const seconds = Math.floor(remainingTime % 60);

        durationDisplay.textContent = `-${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    audio.addEventListener('timeupdate', updateProgressBar);

    playPauseButton.addEventListener('click', () => {
        if (audio.paused) {
            audio.play();
            playPauseButton.textContent = 'Pause';
        } else {
            audio.pause();
            playPauseButton.textContent = 'Play';
        }
    });

    progress.addEventListener('click', (e) => {
        const clickX = e.clientX - progress.getBoundingClientRect().left;
        const progressWidth = progress.offsetWidth;
        const newTime = (clickX / progressWidth) * audio.duration;
        audio.currentTime = newTime;
        updateProgressBar();
    });

    progressKnob.addEventListener('mousedown', () => {
        isDragging = true;

        document.addEventListener('mousemove', handleDragKnob);
        document.addEventListener('mouseup', () => {
            isDragging = false;
            document.removeEventListener('mousemove', handleDragKnob);
        });
    });

    function handleDragKnob(e) {
        if (isDragging) {
            const clickX = e.clientX - progress.getBoundingClientRect().left;
            const progressWidth = progress.offsetWidth;
            let knobPosition = clickX - (progressKnob.offsetWidth / 2);

            if (knobPosition < 0) {
                knobPosition = 0;
            } else if (knobPosition > progressWidth - progressKnob.offsetWidth) {
                knobPosition = progressWidth - progressKnob.offsetWidth;
            }

            const progressPercentage = (knobPosition / (progressWidth - progressKnob.offsetWidth)) * 100;
            const newTime = (progressPercentage / 100) * audio.duration;
            audio.currentTime = newTime;
            progressKnob.style.left = `${knobPosition}px`;
            updateProgressBar();
        }
    }

    nextTrackButton.addEventListener('click', () => {
        currentTrack = (currentTrack + 1) % playlist.length;
        playTrack(currentTrack);
    });

    prevTrackButton.addEventListener('click', () => {
        currentTrack = (currentTrack - 1 + playlist.length) % playlist.length;
        playTrack(currentTrack);
    });

    playlist.forEach((track, index) => {
        track.addEventListener('click', () => {
            currentTrack = index;
            playTrack(currentTrack);
        });
        updateSongInfo();
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const slideshow = document.querySelector('.slideshow');
    const videos = slideshow.querySelectorAll('video');

    let isVideoPlaying = false;

    videos.forEach(video => {
        video.addEventListener('Play', () => {
            isVideoPlaying = true;
            pauseSlideshow();
        });

        video.addEventListener('Pause', () => {
            isVideoPlaying = false;
            if (!isVideoPlaying) {
                resumeSlideshow();
            }
        });

        let isMuted = false;

        const muteButton = document.createElement('button');
        muteButton.classList.add('mute-button');
        muteButton.textContent = 'Mute';
        muteButton.addEventListener('click', () => {
            if (isMuted) {
                video.muted = false;
                muteButton.textContent = 'Mute';
            } else {
                video.muted = true;
                muteButton.textContent = 'Unmute';
            }
            isMuted = !isMuted;
        });

        video.parentElement.appendChild(muteButton);

        const playPauseButton = video.parentElement.querySelector('.play-pause-button');
        if (playPauseButton) {
            playPauseButton.addEventListener('click', () => {
                if (video.paused) {
                    video.play();
                    playPauseButton.textContent = 'Pause';
                } else {
                    video.pause();
                    playPauseButton.textContent = 'Play';
                }
            });
        }
    });

    $(document).ready(function(){
        $('.slideshow').slick({
            autoplay: false,
            autoplaySpeed: 1000,
            arrows: false,
            dots: true
        });
    });
});
