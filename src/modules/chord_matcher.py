import numpy as np
from pathlib import Path
import sys
import collections
import librosa
import json

# Constantes de Áudio
CHUNK = 1024
VOLUME_THRESHOLD = 0.10 
SILENCE_CHUNKS = 10
MIN_CHORDS_CHUNKS = 5
MAX_FREQ_LIMIT = 800
_BASE_DIR = Path(__file__).parent.parent.parent
CHORDS_JSON =  _BASE_DIR / "src\data\chords.json"
RATE = 44100 
SIMILARITY_THRESHOLD = 0.85 

class AudioEventProcessor:
    """
    Processa chunks de áudio em tempo real vindos do WebRTC, 
    detectando eventos de som e retornando a análise quando o silêncio é detectado.
    """
    def __init__(self):
        # O estado que o processador precisa manter entre os frames
        self.silent_chunks_buffer = collections.deque(maxlen=SILENCE_CHUNKS)
        self.recorded_chunks = []
        self.recording = False
        self.reference_chords = load_reference_chords() # Carrega a base de dados uma vez

    def process_audio_chunk(self, audio_buffer: np.ndarray):
        """
        Recebe um único chunk (audio_buffer) do aiortc, atualiza o estado
        e retorna o resultado do acorde se um evento for concluído.
        """
        # 1. Normaliza o array de int16 (WebRTC) para float32 (Librosa)
        # O Librosa espera valores entre -1.0 e 1.0.
        y_raw = audio_buffer.flatten()
        y = y_raw.astype(np.float32) / 32768.0
        
        # 2. Lógica de Detecção de Volume (do seu sound_event_generator)
        volume = np.sqrt(np.mean(y**2))
        is_loud = volume > VOLUME_THRESHOLD
        
        result_to_send = None

        if not self.recording:
            if is_loud:
                print("\n[Acorde] Som detectado, gravando...")
                self.recording = True
                self.recorded_chunks = [y]
                self.silent_chunks_buffer.clear()
        else:
            self.recorded_chunks.append(y)
            self.silent_chunks_buffer.append(not is_loud)
            
            # 3. Verifica o Fim do Evento (Silêncio Prolongado)
            if all(item == True for item in self.silent_chunks_buffer):
                print("[Acorde] Som terminado. Processando...")
                
                if len(self.recorded_chunks) > MIN_CHORDS_CHUNKS:
                    full_audio = np.concatenate(self.recorded_chunks)
                    
                    # 4. Chama a Identificação de Acordes
                    chord, similarity = identify_chord(full_audio, RATE, self.reference_chords)

                    if chord:
                        result_to_send = {
                            "source": "acorde",
                            "status": "OK",
                            "acorde": chord,
                            "similarity": round(similarity, 4)
                        }
                    else:
                        result_to_send = {
                            "source": "acorde",
                            "status": "NO_MATCH",
                            "message": f"Nenhum acorde identificado (Max Sim: {similarity:.4f})"
                        }

                # Reseta o estado do gravador
                self.recording = False
                self.recorded_chunks = []
                self.silent_chunks_buffer.clear()
                print("[Acorde] Aguardando som...")
        
        return result_to_send

def extract_chroma(y, sr):
    """
    Extrai e normaliza o cromagrama médio de um sinal de áudio.
    """
    try:
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        norm = np.linalg.norm(chroma_mean)
        
        if norm > 0:
            chroma_norm = chroma_mean / norm
        else:
            chroma_norm = chroma_mean 
        
        return chroma_norm.tolist()

    except Exception as e:
        print(f"Erro no processamento de audio: {e}", file=sys.stderr)
        return None

def cosine_similarity(v1, v2):
    """
    Calcula a similaridade entre dois cromagramas.
    """
    v1 = np.array(v1)
    v2 = np.array(v2)
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return 0.0
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def load_reference_chords(json_file=CHORDS_JSON):
    try:
        with open(json_file, "r") as f:
            print(f"Base de dados '{json_file}' carregada com sucesso.")
            return json.load(f)
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: Arquivo de referência '{json_file}' não encontrado.", file=sys.stderr)
        print("Por favor, adicione o arquivo 'chords.json' ao diretório.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"ERRO CRÍTICO: Arquivo '{json_file}' está corrompido ou mal formatado.", file=sys.stderr)
        sys.exit(1)

def identify_chord(y, sr, reference_chords):
    print("\n--- INICIANDO NOVA ANÁLISE ---")
    chroma_vector = extract_chroma(y, sr)
    if chroma_vector is None:
        return None, 0.0

    best_match = None
    best_similarity = -1
    all_similarities = {} # Para guardar todos os resultados

    for chord_name, ref_vector in reference_chords.items():
        sim = cosine_similarity(chroma_vector, ref_vector)
        all_similarities[chord_name] = sim # Guarda o resultado
        if sim > best_similarity:
            best_similarity = sim
            best_match = chord_name

    # Imprime a pontuação de TODOS os acordes, do melhor para o pior
    sorted_sims = sorted(all_similarities.items(), key=lambda item: item[1], reverse=True)
    for chord, sim in sorted_sims:
        print(f"  - {chord:<10}: {sim:.4f}")

    if best_similarity >= SIMILARITY_THRESHOLD:
        return best_match, best_similarity
    else:
        return None, best_similarity




