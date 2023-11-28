"use client"
import React, { useEffect, useState } from 'react';
import styles from './spoti.module.css'; // Asegúrate de que las clases de estilo se importan correctamente
import axios from 'axios';


function Spoti() {
  const [activeItem, setActiveItem] = useState('Home');
  const [algorithm, setAlgorithm] = useState('KNN');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [fileUploaded, setFileUploaded] = useState(false);
  const [selectedSong, setSelectedSong] = useState(null);
  const [searchText, setSearchText] = useState('');
  const [searchMethod, setSearchMethod] = useState('My Index');
  const [searchNumber, setSearchNumber] = useState(10);
  const [selectedFile, setSelectedFile] = useState(null);
  const [spotifyAccessToken, setSpotifyAccessToken] = useState(null);

  const fetchTopSongs = async () => {
    try {
        const playlistId = "37i9dQZF1DX9C8KzGEUKV4"; // ID de la lista de reproducción de Spotify
        const response = await axios.get(`http://localhost:5000/spotify/playlist/${playlistId}`, {
            headers: {
                Authorization: `Bearer ${spotifyAccessToken}`,
            },
        });

        // Suponiendo que tu endpoint de backend devuelve un array de canciones
        const topSongs = response.data.map(song => ({
            track_name: song.name,
            track_artist: song.artists.join(", "),
            duration: convertMsToMinutesSeconds(song.duration_ms),
            imageUrl: song.album.images[0].url,
            lyrics: 'From Éxitos Perú' // Ya que Spotify no provee letras
        }));
        
        setSongs(topSongs);
    } catch (error) {
        console.error('Error al obtener las mejores canciones:', error);
    }
};



  const getSpotifyAccessToken = async (code) => {
    try {
      const response = await axios.post('http://localhost:5000/spotify/token', { code });
      const { access_token } = response.data;
      setSpotifyAccessToken(access_token); 
    } catch (error) {
      console.error('Error al obtener el token de Spotify:', error);
    }
  };

  useEffect(() => {

    if (typeof window !== 'undefined') {
      const queryParams = new URLSearchParams(window.location.search);
      const code = queryParams.get('code');

      if (code && !spotifyAccessToken) {
        getSpotifyAccessToken(code);
      }
      if (spotifyAccessToken) {
        fetchTopSongs(); 
    }
    }
  }, [spotifyAccessToken]);

  const [songs, setSongs] = useState([
  ]);

  const handleHomeClick = () => {
    setActiveItem('Home');
    // Restablece las canciones a su estado inicial
    fetchTopSongs();
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      console.log(file);
      setUploadProgress(0);
      setIsUploading(true);
      setFileUploaded(false);
  
      // Simula la carga del archivo
      const interval = setInterval(() => {
        setUploadProgress((oldProgress) => {
          const newProgress = Math.min(oldProgress + 10, 100);
          if (newProgress === 100) {
            clearInterval(interval);
            setIsUploading(false);
            setFileUploaded(true); // Indica que el archivo se ha cargado
          }
          return newProgress;
        });
      }, 500);
    }
  };

  const defaultRightContent = (
    <div className={styles.defaultRight}>
      <img src="https://cdn.discordapp.com/attachments/1155323431915630594/1178600841394016317/6532493.png?ex=6576bc91&is=65644791&hm=d5d99fef558ed5539b9ed9f59b1358d0d5a67fdd3d5a3c193c2b04247632f3dd&" alt="Bienvenido" className={styles.defaultImage} />
      <div className={styles.welcomeMessage}>
        Bienvenido a Pineapple Music! Elige una canción para visualizar su letra. No te acuerdas el nombre 
        de la canción? No hay problema, también contamos con un buscador por audio muy útil para usted 😉👌.
      </div>
    </div>
  );

  const menuItems = [
    { name: 'Home', icon: '🏠' },
    { name: 'Buscar', icon: '🔍' },
    { name: 'Your Library', icon: '📚' }
  ];

  const playlists = [
    { name: 'Top 100 Peru', creator: 'Playlist by Luis Golac' },
    { name: 'Daily Mix', creator: 'Playlist by Sebastian Loza' },
    { name: 'Viva Latino', creator: 'Playlist by Aaron Coorahua' },
    { name: 'Hits Urbanos', creator: 'Playlist by Cesar Pajuelo' },
    { name: 'Musica Sad', creator: 'Playlist by Gonzalo Rodriguez' }
  ];

  const handleSongClick = (song) => {
    setSelectedSong(song);
  };

  const handleSearchChange = (e) => {
    setSearchText(e.target.value);
  };

  const handleNumberChange = (e) => {
    setSearchNumber(e.target.value);
  };

  const handleMethodChange = (e) => {
    setSearchMethod(e.target.value);
  };

  const searchSongs = async () => {
    setActiveItem('Buscar');
    try {
      let endpoint = '';
      if (searchMethod === 'PostgreSQL') {
        endpoint = 'http://127.0.0.1:5000/psql';
      } else if (searchMethod === 'MyIndex') {
        endpoint = 'http://127.0.0.1:5000/invert_index';
      }
  
      const response = await axios.post(endpoint, {
        textQuery: searchText,
        topK: searchNumber
      });
  
      if (response.status === 200) {
        const imagePromises = response.data.map(song => getTrackImageUrl(song.track_id));
        const images = await Promise.all(imagePromises);
  
        const updatedSongs = response.data.map((song, index) => ({
          ...song,
          duration: convertMsToMinutesSeconds(song.duration_ms),
          imageUrl: images[index] // Asegúrate de que el orden de las imágenes coincida con el de las canciones
        }));
  
        setSongs(updatedSongs);
      } else {
        console.error('Error en la búsqueda:', response.status);
      }
    } catch (error) {
      console.error('Error en la conexión:', error);
    }
  };

  const convertMsToMinutesSeconds = (ms) => {
    const minutes = Math.floor(ms / 60000);
    const seconds = ((ms % 60000) / 1000).toFixed(0);
    return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
  };

  const handleScanClick = async () => {
    setActiveItem('Your Library');
    const formData = new FormData();
    console.log('Botón escanear presionado');
    if (selectedFile) {
      formData.append('audio', selectedFile);
    }
    formData.append('json', JSON.stringify({ topK: searchNumber }));
    let endpoint = '';
    switch (algorithm) {
      case 'KNN':
        endpoint = '/knn'; // Asegúrate de que la ruta esté en minúsculas si así está definida en el backend
        break;
      case 'FAISS':
        endpoint = '/faiss';
        break;
      case 'RTREE':
        endpoint = '/rtree';
        break;
      default:
        console.error('Algoritmo no reconocido');
        return;
    }
    try {
      const response = await axios.post(`http://127.0.0.1:5000${endpoint}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
  
      if (response.status === 200) {
        const imagePromises = response.data.map(song => getTrackImageUrl(song.track_id));
        const images = await Promise.all(imagePromises);
        const searchResults = response.data.map((song) => ({
          ...song,
          duration: convertMsToMinutesSeconds(song.duration_ms),
          imageUrl: images[index]
        }));
        setSongs(searchResults);
      } else {
        console.error('Error en la búsqueda:', response.status);
      }
    } catch (error) {
      console.error('Error en la conexión:', error);
    }
  };

  const getTrackImageUrl = async (trackId) => {
    try {
      const cleanedTrackId = trackId.trim(); // Esto eliminará los espacios al principio y al final
      const response = await axios.get(`http://localhost:5000/spotify/track/${cleanedTrackId}`, {
        headers: {
          Authorization: `Bearer ${spotifyAccessToken}`,
        },
      });
      return response.data.image_url;
    } catch (error) {
      console.error('Error al obtener la imagen del track:', error);
      return ''; 
    }
  };

  const defaultPlaylistImageUrl = "https://cdn.discordapp.com/attachments/1166998304937222166/1178931502222938122/music-playlist-icon-5.jpg?ex=6577f085&is=65657b85&hm=3f7283d17be86c77e169b855044f45e97402d6027b486d7fe0e61e6f0a4fca50&";
  
  return(
    <main className={styles.container}>
      {/*<div className={styles.header}> 
        <h1>Pineapple Music</h1>
        <img src="https://cdn.discordapp.com/attachments/1155323431915630594/1178600841394016317/6532493.png?ex=6576bc91&is=65644791&hm=d5d99fef558ed5539b9ed9f59b1358d0d5a67fdd3d5a3c193c2b04247632f3dd&" alt="Bienvenido" className={styles.logo} />
  </div>*/}
      <div className={styles.content}>
        <div className={styles.columns}>
          <div className={`${styles.columnLeft} ${styles.columnScroll}`}>
              {menuItems.map(item => (
              <div key={item.name} 
                  className={`${styles.item} ${activeItem === item.name ? styles.activeItem : ''}`} 
                  onClick={() => item.name === 'Home' ? handleHomeClick() : setActiveItem(item.name)}>
                <span className={styles.icon}>{item.icon}</span>
                <span className={styles.text}>{item.name}</span>
              </div>
            ))}
            <div className={styles.playlists}>
                {playlists.map((playlist, index) => (
                  <div key={index} className={styles.playlistItem}>
                    <img src={defaultPlaylistImageUrl} alt={playlist.name} className={styles.playlistImage} />
                    <div>
                      <div className={styles.playlistName}>{playlist.name}</div>
                      <div className={styles.playlistCreator}>{playlist.creator}</div>
                    </div>
                  </div>
                ))}
            </div>
          
            <div className={styles.fileContainer}>
              <input
                type="file"
                onChange={handleFileUpload}
                className={styles.hiddenFileInput}
                // Agrega la clave "key" para reiniciar el componente input después de una carga
                key={uploadProgress}
              />
              <button className={styles.uploadButton}>Upload</button>
              {isUploading && (
                <div className={styles.progressBarContainer}>
                  <div className={styles.progressBar} style={{ width: `${uploadProgress}%` }}></div>
                </div>
              )}
              
              
            </div>
            <button className={styles.scanButton} onClick={handleScanClick}>Escanear</button>
            <select
              value={algorithm}
              onChange={(e) => setAlgorithm(e.target.value)}
              className={`${styles.selectField} ${styles.selectInput}`}
            >
              <option value="KNN">KNN</option>
              <option value="FAISS">FAISS</option>
              <option value="RTREE">RTREE</option>
            </select>
            <div className={styles.branding}>
                <img src="https://cdn.discordapp.com/attachments/1155323431915630594/1178600841394016317/6532493.png" alt="Logo" className={styles.logo} />
                <h1 className={styles.title}>Pineapple Music</h1>
              </div>
          </div>
          <div className={`${styles.columnMiddle} ${styles.columnScroll}`}>
          <div className={styles.searchContainer}>
              <input
                type="text"
                placeholder="Search"
                value={searchText}
                onChange={handleSearchChange}
                className={`${styles.inputField} ${styles.searchBar}`} 
              />
              
              <input
                type="number"
                placeholder="Top K"
                value={searchNumber} 
                onChange={handleNumberChange} 
                className={styles.inputField}
              />
              
              <select 
                className={`${styles.selectField} ${styles.selectInput}`}
                value={searchMethod}
                onChange={handleMethodChange}
              >
                <option value="MyIndex">My Index</option>
                <option value="PostgreSQL">PostgreSQL</option>
              </select>
              <button onClick={searchSongs} className={styles.searchButton}>Buscar</button>
            </div>
            
            <div className={styles.songsContainer}>
              {songs.map((song, index) => (
                <div key={index} className={styles.songCard} onClick={() => handleSongClick(song)}>
                  <img src={song.imageUrl} alt={song.title} className={styles.songImage} />
                  <div className={styles.songDetails}>
                    <div className={styles.songTitle}>{song.track_name}</div>
                    <div className={styles.songArtist}>{song.track_artist}</div>
                    <div className={styles.songDuration}>{song.duration}</div>   
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className={`${styles.columnRight} ${styles.columnScroll}`}>
            {selectedSong ? (
              <div className={styles.songContent}>
                <img src={selectedSong.imageUrl} alt={selectedSong.title} className={styles.songImage} />
                <div className={styles.songDetails}>
                  <div className={styles.songTitle}>{selectedSong.track_name}</div>
                  <div className={styles.songArtist}>{selectedSong.track_artist}</div>
                  <div className={styles.songDuration}>{selectedSong.duration}</div>
                </div>
                <div className={styles.songLyrics}>
                  {selectedSong.lyrics}
                </div>
              </div>
            ) : (
              defaultRightContent
            )}
          </div>
        </div>
      </div>
    </main>
  );
}

export default Spoti;