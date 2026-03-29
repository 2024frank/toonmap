import { useState, useRef } from 'react';
import './App.css';

interface ToonMapRequest {
  address: string;
  radius_meters: number;
  pitch: number;
  bearing: number;
  style: string;
}

interface Landmark {
  name: string;
  type: string;
  lat: number;
  lon: number;
}

interface ToonMapResponse {
  address: string;
  satellite_image_url: string;
  cartoon_image_base64: string;
  toonmap_image_base64: string;
  landmarks: Landmark[];
  parameters: {
    radius_meters: number;
    pitch: number;
    bearing: number;
    style: string;
    zoom: number;
  };
}

interface Country {
  code: string;
  name: string;
  flag: string;
}

const COUNTRIES: Country[] = [
  { code: 'US', name: 'United States', flag: '🇺🇸' },
  { code: 'GB', name: 'United Kingdom', flag: '🇬🇧' },
  { code: 'FR', name: 'France', flag: '🇫🇷' },
  { code: 'DE', name: 'Germany', flag: '🇩🇪' },
  { code: 'IT', name: 'Italy', flag: '🇮🇹' },
  { code: 'ES', name: 'Spain', flag: '🇪🇸' },
  { code: 'CA', name: 'Canada', flag: '🇨🇦' },
  { code: 'AU', name: 'Australia', flag: '🇦🇺' },
  { code: 'JP', name: 'Japan', flag: '🇯🇵' },
  { code: 'CN', name: 'China', flag: '🇨🇳' },
  { code: 'BR', name: 'Brazil', flag: '🇧🇷' },
  { code: 'IN', name: 'India', flag: '🇮🇳' },
];

const LANDMARK_ICONS: Record<string, string> = {
  place_of_worship: '⛪',
  park: '🌳',
  museum: '🏛️',
  historic: '🏺',
  school: '🎓',
  hospital: '🏥',
  restaurant: '🍽️',
  default: '📍',
};

const API_BASE = 'http://localhost:8000';

interface VerifiedLocation {
  place_name: string;
  lat: number;
  lng: number;
}

const PROGRESS_STAGES = [
  { percent: 12, message: 'Fetching satellite imagery…' },
  { percent: 28, message: 'Downloading streets layer…' },
  { percent: 44, message: 'Compositing reference layers…' },
  { percent: 58, message: 'Preparing AI input…' },
  { percent: 72, message: 'AI is transforming your map…' },
  { percent: 88, message: 'Overlaying landmarks…' },
  { percent: 96, message: 'Finalising ToonMap…' },
];

function Spinner() {
  return (
    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
    </svg>
  );
}

function App() {
  const [country, setCountry] = useState<Country>(COUNTRIES[0]);
  const [address, setAddress] = useState('135 W Lorain Street, Oberlin, Ohio');
  const [radius, setRadius] = useState(500);
  const [showLabels, setShowLabels] = useState(false);
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [verified, setVerified] = useState<VerifiedLocation | null>(null);
  const [result, setResult] = useState<ToonMapResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const resultRef = useRef<HTMLDivElement>(null);

  const verifyAddress = async () => {
    setVerifying(true);
    setError(null);
    setVerified(null);
    try {
      const res = await fetch(`${API_BASE}/fetch-map`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address: `${address}, ${country.name}`, radius_meters: radius, pitch: 60, bearing: 0 }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || 'Address not found');
      const data = await res.json();
      setVerified({ place_name: data.center.place_name, lat: data.center.lat, lng: data.center.lng });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to verify address');
    } finally {
      setVerifying(false);
    }
  };

  const generateToonMap = async () => {
    setLoading(true);
    setError(null);
    setProgress(0);
    setProgressMessage(PROGRESS_STAGES[0].message);

    let stage = 0;
    const interval = setInterval(() => {
      if (stage < PROGRESS_STAGES.length) {
        setProgress(PROGRESS_STAGES[stage].percent);
        setProgressMessage(PROGRESS_STAGES[stage].message);
        stage++;
      }
    }, 8000);

    try {
      const res = await fetch(`${API_BASE}/toonmap`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          address: `${address}, ${country.name}`,
          radius_meters: radius,
          pitch: 60,
          bearing: 0,
          style: '3d_cartoon',
        } as ToonMapRequest),
      });

      clearInterval(interval);
      setProgress(100);
      setProgressMessage('Complete!');

      if (!res.ok) throw new Error((await res.json()).detail || 'Failed to generate ToonMap');

      const data: ToonMapResponse = await res.json();
      setResult(data);
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
    } catch (err) {
      clearInterval(interval);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
      setTimeout(() => { setProgress(0); setProgressMessage(''); }, 2000);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!verified) verifyAddress();
    else generateToonMap();
  };

  const handleAddressChange = (v: string) => {
    setAddress(v);
    setVerified(null);
    setResult(null);
  };

  const downloadImage = (base64: string, name: string) => {
    const a = document.createElement('a');
    a.href = `data:image/png;base64,${base64}`;
    a.download = name;
    a.click();
  };

  return (
    <div className="min-h-screen bg-[#08080c] grid-bg overflow-x-hidden">

      {/* Ambient orbs */}
      <div className="orb w-[600px] h-[600px] top-[-200px] left-[-200px] bg-violet-600/20" />
      <div className="orb w-[500px] h-[500px] top-[20%] right-[-150px] bg-fuchsia-600/15" />
      <div className="orb w-[400px] h-[400px] bottom-[10%] left-[30%] bg-indigo-600/10" />

      {/* Nav */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-5 border-b border-white/5">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🗺️</span>
          <span className="font-display text-xl font-bold tracking-tight">ToonMap</span>
        </div>
        <div className="hidden md:flex items-center gap-1 text-sm text-white/40">
          <span className="pulse-dot inline-block w-2 h-2 rounded-full bg-emerald-400 mr-2" />
          AI-powered map transformation
        </div>
      </nav>

      {/* Hero */}
      <section className="relative z-10 text-center px-4 pt-20 pb-16">
        <div className="inline-flex items-center gap-2 glass rounded-full px-4 py-1.5 text-sm text-white/60 mb-8">
          <span className="text-violet-400">✦</span>
          Powered by gpt-image-1 + Mapbox
        </div>
        <h1 className="font-display text-5xl md:text-7xl font-extrabold leading-tight mb-6 tracking-tight">
          Turn Any Address Into<br />
          <span className="gradient-text">Cartoon Art</span>
        </h1>
        <p className="text-lg md:text-xl text-white/50 max-w-xl mx-auto leading-relaxed">
          Type a real-world address and get a stunning 3D illustrated map in under a minute.
          Every street, building, and landmark — rendered in vivid cartoon style.
        </p>
      </section>

      {/* Form */}
      <div className="relative z-10 max-w-xl mx-auto px-4 pb-16">
        <div className="glass rounded-3xl p-8 shadow-2xl shadow-violet-950/30">
          <form onSubmit={handleSubmit} className="space-y-5">

            {/* Country */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-white/40 uppercase tracking-wider">Country</label>
              <select
                value={country.code}
                onChange={(e) => {
                  const c = COUNTRIES.find(x => x.code === e.target.value);
                  if (c) { setCountry(c); setVerified(null); setResult(null); }
                }}
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white
                           focus:outline-none focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/30
                           transition-all text-sm cursor-pointer"
              >
                {COUNTRIES.map(c => (
                  <option key={c.code} value={c.code} className="bg-[#18181b]">
                    {c.flag} {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Address */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-white/40 uppercase tracking-wider">Address or Location</label>
              <input
                type="text"
                value={address}
                onChange={(e) => handleAddressChange(e.target.value)}
                placeholder="e.g., Times Square, New York…"
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white
                           placeholder-white/20 focus:outline-none focus:border-violet-500/60
                           focus:ring-1 focus:ring-violet-500/30 transition-all text-sm"
                required
              />
            </div>

            {/* Verified badge */}
            {verified && (
              <div className="fade-up flex items-start gap-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4">
                <span className="text-emerald-400 text-lg mt-0.5">✓</span>
                <div className="flex-1 min-w-0">
                  <p className="text-emerald-300 text-sm font-semibold truncate">{verified.place_name}</p>
                  <p className="text-emerald-500/70 text-xs font-mono mt-0.5">
                    {verified.lat.toFixed(5)}, {verified.lng.toFixed(5)}
                  </p>
                </div>
                <button type="button" onClick={() => setVerified(null)}
                  className="text-emerald-500/60 hover:text-emerald-400 text-xs transition-colors shrink-0">
                  Change
                </button>
              </div>
            )}

            {/* Radius */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-white/40 uppercase tracking-wider">Radius</label>
                <span className="text-sm font-semibold text-violet-300">{radius}m</span>
              </div>
              <input
                type="range" min="100" max="2000" step="50" value={radius}
                onChange={(e) => { setRadius(Number(e.target.value)); setVerified(null); setResult(null); }}
                className="w-full cursor-pointer"
                style={{
                  background: `linear-gradient(to right, #a78bfa ${(radius - 100) / 19}%, rgba(255,255,255,0.1) ${(radius - 100) / 19}%)`
                }}
              />
              <div className="flex justify-between text-xs text-white/20">
                <span>100m</span><span>1000m</span><span>2000m</span>
              </div>
            </div>

            {/* Labels toggle */}
            <div className="flex items-center justify-between py-1">
              <span className="text-sm text-white/50">Show landmark labels</span>
              <button
                type="button"
                onClick={() => setShowLabels(!showLabels)}
                className={`relative w-12 h-6 rounded-full transition-all duration-300 ${showLabels ? 'bg-violet-600' : 'bg-white/10'}`}
              >
                <span className={`absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform duration-300 ${showLabels ? 'translate-x-6' : ''}`} />
              </button>
            </div>

            {/* CTA button */}
            <button
              type="submit"
              disabled={loading || verifying || !address.trim()}
              className={`w-full py-4 rounded-xl font-semibold text-base transition-all duration-200
                         disabled:opacity-40 disabled:cursor-not-allowed
                         flex items-center justify-center gap-2
                         ${!verified
                           ? 'bg-white/10 hover:bg-white/15 text-white border border-white/10 hover:border-white/20'
                           : 'bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 text-white shadow-lg shadow-violet-900/40 hover:shadow-violet-900/60 hover:scale-[1.01]'
                         }`}
            >
              {verifying ? <><Spinner /> Verifying address…</> :
               loading   ? <><Spinner /> Generating ToonMap…</> :
               !verified ? <><span className="text-white/60">🔍</span> Verify Address</> :
                           <><span>✦</span> Generate ToonMap</>}
            </button>
          </form>

          {/* Error */}
          {error && (
            <div className="fade-up mt-5 bg-red-500/10 border border-red-500/20 rounded-xl p-4">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          {/* Progress */}
          {loading && (
            <div className="fade-up mt-6 space-y-3">
              <div className="flex justify-between items-center">
                <p className="text-sm text-white/60">{progressMessage}</p>
                <p className="text-sm font-semibold text-violet-300">{progress}%</p>
              </div>
              <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full progress-bar transition-all duration-700 ease-out"
                  style={{
                    width: `${progress}%`,
                    background: 'linear-gradient(90deg, #7c3aed, #a855f7, #ec4899)',
                  }}
                />
              </div>
              <p className="text-xs text-white/20 text-center">AI transformation takes 30–60 seconds</p>
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      {result && (
        <div ref={resultRef} className="relative z-10 max-w-7xl mx-auto px-4 pb-24 fade-up">

          {/* Section header */}
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 glass rounded-full px-4 py-1.5 text-sm text-white/50 mb-4">
              <span className="text-emerald-400">✓</span> ToonMap generated
            </div>
            <h2 className="font-display text-3xl md:text-4xl font-bold text-white">{result.address}</h2>
          </div>

          {/* Main comparison */}
          <div className="grid md:grid-cols-2 gap-5 mb-6">
            {/* Satellite */}
            <div className="glass rounded-2xl overflow-hidden group">
              <div className="flex items-center justify-between px-5 py-4 border-b border-white/5">
                <div>
                  <p className="text-xs text-white/30 uppercase tracking-wider font-semibold">Satellite</p>
                  <p className="text-white font-semibold mt-0.5">Original View</p>
                </div>
                <span className="text-2xl">🛰️</span>
              </div>
              <div className="p-3">
                <img
                  src={result.satellite_image_url}
                  alt="Satellite"
                  className="w-full rounded-xl"
                />
              </div>
            </div>

            {/* Cartoon */}
            <div className="glass rounded-2xl overflow-hidden group">
              <div className="flex items-center justify-between px-5 py-4 border-b border-white/5">
                <div>
                  <p className="text-xs text-white/30 uppercase tracking-wider font-semibold">ToonMap</p>
                  <p className="text-white font-semibold mt-0.5">
                    {showLabels ? 'With Landmark Labels' : 'Cartoon Render'}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => downloadImage(
                      showLabels ? result.toonmap_image_base64 : result.cartoon_image_base64,
                      'toonmap.png'
                    )}
                    className="text-xs text-white/40 hover:text-white/80 transition-colors glass rounded-lg px-3 py-1.5"
                  >
                    ↓ Save
                  </button>
                  <span className="text-2xl">🎨</span>
                </div>
              </div>
              <div className="p-3">
                <img
                  src={`data:image/png;base64,${showLabels ? result.toonmap_image_base64 : result.cartoon_image_base64}`}
                  alt="ToonMap"
                  className="w-full rounded-xl"
                />
              </div>
            </div>
          </div>

          {/* Landmarks */}
          {result.landmarks.length > 0 && (
            <div className="glass rounded-2xl p-6 mb-6">
              <p className="text-xs text-white/30 uppercase tracking-wider font-semibold mb-4">
                {result.landmarks.length} Landmarks Detected
              </p>
              <div className="flex flex-wrap gap-2">
                {result.landmarks.map((lm, i) => (
                  <div key={i} className="flex items-center gap-2 bg-white/5 hover:bg-white/8 border border-white/8
                                          rounded-xl px-3 py-2 transition-colors">
                    <span className="text-base">{LANDMARK_ICONS[lm.type] ?? LANDMARK_ICONS.default}</span>
                    <div>
                      <p className="text-sm font-medium text-white/80 leading-none">{lm.name}</p>
                      <p className="text-xs text-white/30 mt-0.5 capitalize">{lm.type.replace(/_/g, ' ')}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Meta */}
          <div className="flex flex-wrap gap-3 justify-center">
            {[
              { label: 'Radius', value: `${result.parameters.radius_meters}m` },
              { label: 'Zoom', value: `×${result.parameters.zoom}` },
              { label: 'Pitch', value: `${result.parameters.pitch}°` },
              { label: 'Style', value: result.parameters.style.replace(/_/g, ' ') },
            ].map(({ label, value }) => (
              <div key={label} className="glass rounded-xl px-4 py-2 text-center min-w-[80px]">
                <p className="text-xs text-white/25 uppercase tracking-wider">{label}</p>
                <p className="text-sm font-semibold text-white/70 mt-0.5 capitalize">{value}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/5 py-8 text-center text-white/20 text-sm">
        ToonMap — AI Map Art Generator
      </footer>
    </div>
  );
}

export default App;
