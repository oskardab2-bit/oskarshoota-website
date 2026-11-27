# oskarshoota Website

Statische Website (Ordner `public/`), gehostet auf Netlify.
Eine GitHub Action (`.github/workflows/update.yml`) prüft jeden Tag die Spotify-Playlist
„Mix/Master/Rec/Prod by oskarshoota“ und aktualisiert `public/refs.json` samt Covern.
Songs, die aus der Playlist verschwinden, verschwinden auch von der Website.
Manuell auslösen: Tab „Actions“ → „Referenzen aktualisieren“ → „Run workflow“.
