"use client"
import { useState } from 'react';
import styles from './page.module.css'; // Asegúrate de tener este archivo con los estilos adecuados.
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import { useRouter } from 'next/navigation';

export default function Home() {
  // useRouter puede ser utilizado si necesitas manipular la ruta, por ejemplo después de un login exitoso.
  const router = useRouter();

  const handleSpotifyAuth = () => {
    const scopes = 'user-read-private user-read-email';
    const clientId = '80aede95556043b8aac562834bd2b270'; // Reemplaza esto con tu client ID de Spotify.
    const redirectUri = `${window.location.origin}/spoti`; // Asegúrate de que esta URI de redirección esté registrada en tu aplicación de Spotify.
    const spotifyAuthUrl = `https://accounts.spotify.com/authorize?client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${encodeURIComponent(scopes)}&response_type=code&show_dialog=true`;
    window.location.href = spotifyAuthUrl;
  };

  return (
    <div className={styles.background}>
      <main className={styles.main}>
        <div className={styles.loginContainer}>
          <div className={styles.logoContainer}>
            <img src="https://cdn.discordapp.com/attachments/1155323431915630594/1178600841394016317/6532493.png?ex=6576bc91&is=65644791&hm=d5d99fef558ed5539b9ed9f59b1358d0d5a67fdd3d5a3c193c2b04247632f3dd&" alt="Music App Logo" width={120} height={120} />
          </div>
          <div className={styles.formContainer}>
            <button 
              type="button" 
              className={`btn btn-danger btn-lg ${styles.loginButton}`} // Clases de Bootstrap para un botón grande y rojo
              onClick={handleSpotifyAuth}
            >
              <i className="bi bi-spotify"></i> Ingresar
            </button>
          </div>
          <div className={styles.musicNotes}>
            <i className="bi bi-music-note-beamed"></i>
            <i className="bi bi-music-note-list"></i>
          </div>
        </div>
      </main>
    </div>
  );
}
