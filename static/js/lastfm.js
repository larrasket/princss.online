// Last.fm integration for dynamic listening status
// Uses Last.fm API to fetch current/recent tracks for user 'larrasket'

const LASTFM_API_KEY = "efa2958594802122ccd0190743a51cdd";
const LASTFM_USER = "larrasket";
const LASTFM_API_URL = "https://ws.audioscrobbler.com/2.0/";

async function fetchCurrentTrack() {
    const apiUrl = `${LASTFM_API_URL}?method=user.getrecenttracks&user=${LASTFM_USER}&api_key=${LASTFM_API_KEY}&format=json&limit=1`;

    // Try direct API call first (Last.fm may support CORS)
    try {
        const response = await fetch(apiUrl);
        if (response.ok) {
            const data = await response.json();
            const track = parseTrackData(data);
            if (track) return track;
        }
    } catch (error) {
        console.warn("Direct Last.fm API call failed:", error);
    }

    // Fallback: try CORS proxies
    const corsProxies = [
        { url: "https://api.allorigins.win/get?url=", needsEncode: true, unwrap: true },
        { url: "https://corsproxy.io/?", needsEncode: false, unwrap: false },
    ];

    for (const proxy of corsProxies) {
        try {
            const proxiedUrl = proxy.needsEncode
                ? `${proxy.url}${encodeURIComponent(apiUrl)}`
                : `${proxy.url}${apiUrl}`;

            const response = await fetch(proxiedUrl);
            if (!response.ok) continue;

            let data = await response.json();
            if (proxy.unwrap && data.contents) {
                data = JSON.parse(data.contents);
            }

            const track = parseTrackData(data);
            if (track) return track;
        } catch (error) {
            console.warn(`CORS proxy ${proxy.url} failed:`, error);
            continue;
        }
    }

    console.warn("All Last.fm API methods failed");
    return null;
}

function parseTrackData(data) {
    if (!data.recenttracks || !data.recenttracks.track) return null;
    
    const track = Array.isArray(data.recenttracks.track)
        ? data.recenttracks.track[0]
        : data.recenttracks.track;

    if (!track) return null;

    return {
        artist: track.artist["#text"] || track.artist,
        title: track.name,
        album: track.album["#text"] || track.album,
        image: track.image
            ? track.image[2] && track.image[2]["#text"]
                ? track.image[2]["#text"]
                : track.image[1]["#text"]
            : "",
        url: track.url,
        nowPlaying: track["@attr"] && track["@attr"].nowplaying === "true",
    };
}

function updateMusicWidget(trackData) {
    const trackArt = document.getElementById("trackart");
    const trackArtist = document.getElementById("trackartist");
    const trackTitle = document.getElementById("tracktitle");
    const loadingIndicator = document.querySelector(".loading-indicator");

    if (!trackArt || !trackArtist || !trackTitle) {
        console.warn("Music widget elements not found");
        return;
    }

    // Hide loading indicator
    if (loadingIndicator) {
        loadingIndicator.style.display = "none";
    }

    if (trackData) {
        // Update album art
        if (trackData.image) {
            trackArt.src = trackData.image;
            trackArt.alt = `${trackData.album} by ${trackData.artist}`;
        }

        // Update artist
        trackArtist.textContent = trackData.artist;
        trackArtist.title = `Artist: ${trackData.artist}`;

        // Update track title
        trackTitle.textContent = trackData.title;
        trackTitle.href = trackData.url;
        trackTitle.title = `${trackData.title} by ${trackData.artist}`;

        // Add "now playing" indicator if currently playing
        const titleElement = document.querySelector(".music-section .title");
        if (titleElement) {
            titleElement.textContent = trackData.nowPlaying
                ? "now playing:"
                : "recently played:";
        }
    }
}

// Initialize when page loads
document.addEventListener("DOMContentLoaded", async function () {
    // Only run on music page
    if (!document.querySelector(".music-section")) return;

    const loadingIndicator = document.querySelector(".loading-indicator");
    if (loadingIndicator) {
        loadingIndicator.style.display = "block";
    }

    const trackData = await fetchCurrentTrack();
    updateMusicWidget(trackData);
});

// Optionally update every few minutes
setInterval(async function () {
    if (document.querySelector(".music-section")) {
        const trackData = await fetchCurrentTrack();
        if (trackData) {
            updateMusicWidget(trackData);
        }
    }
}, 300000); // Update every 5 minutes
