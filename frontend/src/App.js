import './App.css';
import React, { useEffect, useState, useRef } from 'react';
import { supabase } from './supabaseClient';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer, BarChart, XAxis, YAxis, Bar } from 'recharts';
import Login from './Login';

function App() {
  // TÜM HOOKLAR EN ÜSTE, KOŞULSUZ VE TEK SEFERDE!
  const [session, setSession] = useState(null);
  const [segments, setSegments] = useState([]);
  const [search, setSearch] = useState("");
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState("");
  const fileInputRef = useRef(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });
    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });
    return () => {
      listener?.subscription.unsubscribe();
    };
  }, []);
  // Dosya analiz için API'ye gönder
  async function handleAnalyze() {
    if (!files.length) return;
    setUploading(true);
    setUploadMsg("");
    const formData = new FormData();
    files.forEach((f) => formData.append('files', f));
    try {
      const resp = await fetch('http://localhost:8000/analyze-file', {
        method: 'POST',
        body: formData,
      });
      if (resp.ok) {
        const data = await resp.json();
        setUploadMsg('Analiz başarılı! Sonuçlar tabloya eklendi.');
        setSegments(data.result); // Analiz edilen dosyaları tabloya aktar
      } else {
        setUploadMsg('Analiz sırasında hata oluştu.');
      }
    } catch (err) {
      setUploadMsg('Sunucuya ulaşılamadı.');
    }
    setUploading(false);
    setFiles([]);
  }



  useEffect(() => {
    async function fetchSegments() {
      const { data, error } = await supabase
        .from('user_segments')
        .select('*')
        .order('created_at', { ascending: false })
      if (error) {
        console.error('Supabase error:', error)
      } else {
        setSegments(data)
        console.log('Supabase data:', data)
      }
    }
    fetchSegments();

    // Supabase Realtime ile canlı güncelleme
    const channel = supabase.channel('user_segments_realtime')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'user_segments',
      }, payload => {
        fetchSegments();
      })
      .subscribe();

    return () => {
      channel.unsubscribe();
    };
  }, []);

  // Filtreli segmentler
  const filteredSegments = segments.filter(seg => {
    const query = search.toLowerCase();
    return (
      (seg.user_id && seg.user_id.toLowerCase().includes(query)) ||
      (seg.segment && seg.segment.toLowerCase().includes(query)) ||
      (seg.prediction !== undefined && String(seg.prediction).includes(query)) ||
      (seg.created_at && new Date(seg.created_at).toLocaleString('tr-TR').includes(query))
    );
  });

  // Segment dağılımı için veri hazırla
  const segmentCounts = segments.reduce((acc, seg) => {
    acc[seg.segment] = (acc[seg.segment] || 0) + 1;
    return acc;
  }, {});
  const pieData = Object.entries(segmentCounts).map(([segment, count]) => ({ name: segment, value: count }));
  const PIE_COLORS = ["#6EC6FF", "#FFD56E", "#FF6E6E", "#A7F0BA", "#B5A7F0", "#F0A7E6", "#F0E3A7"];

  // Segmentlere göre ortalama prediction
  const segmentPreds = {};
  segments.forEach(seg => {
    if (!segmentPreds[seg.segment]) segmentPreds[seg.segment] = [];
    segmentPreds[seg.segment].push(Number(seg.prediction));
  });
  const barData = Object.entries(segmentPreds).map(([segment, preds]) => ({
    segment,
    avgPrediction: preds.reduce((a, b) => a + b, 0) / preds.length
  }));

  // Toplam kullanıcı sayısı
  const totalUsers = segments.length;

  if (!session) {
    return <Login onLogin={() => window.location.reload()} />;
  }

  // Avatar harfi (email baş harfi)
  const userInitial = session?.user?.email ? session.user.email[0].toUpperCase() : "U";

  // Dosya seçildiğinde
  function handleFileChange(e) {
    setFiles(Array.from(e.target.files));
    setUploadMsg("");
  }

  // Dosya analiz için API'ye gönder
  async function handleAnalyze() {
    if (!files.length) return;
    setUploading(true);
    setUploadMsg("");
    const formData = new FormData();
    files.forEach((f) => formData.append('files', f));
    try {
      const resp = await fetch('http://localhost:8000/analyze-file', {
        method: 'POST',
        body: formData,
      });
      if (resp.ok) {
        const data = await resp.json();
        setUploadMsg('Analiz başarılı! Sonuçlar tabloya eklendi.');
        setSegments(data.result); // Analiz edilen dosyaları tabloya aktar
      } else {
        setUploadMsg('Analiz sırasında hata oluştu.');
      }
    } catch (err) {
      setUploadMsg('Sunucuya ulaşılamadı.');
    }
    setUploading(false);
    setFiles([]);
  }

  return (
    <div>
      {/* Apple tarzı üst bar */}
      <div className="topbar">
        <span className="dashboard-title">Kullanıcı Segmentleri Dashboard</span>
        <div style={{display:'flex',alignItems:'center',gap:14}}>
          <span className="user-avatar">{userInitial}</span>
          <button style={{background:'#fff',border:'1.5px solid #e0e2e7',borderRadius:10,padding:'7px 18px',fontWeight:600,fontSize:'1rem',color:'#007aff',cursor:'pointer',boxShadow:'0 1.5px 6px 0 rgba(0,0,0,0.03)'}} onClick={async()=>{await supabase.auth.signOut();window.location.reload();}}>Çıkış Yap</button>
        </div>
      </div>

      {/* Dosya Yükleme Alanı */}
      <div className="file-upload-card">
        <label className="file-upload-label" htmlFor="file-upload-input">
          Kullanıcı Dosyası Yükle (CSV veya JSON)
        </label>
        <input
          ref={fileInputRef}
          id="file-upload-input"
          className="file-upload-input"
          type="file"
          accept=".csv,.json"
          multiple
          onChange={handleFileChange}
          disabled={uploading}
        />
        <button
          type="button"
          className="file-upload-btn"
          disabled={uploading}
          onClick={() => fileInputRef.current && fileInputRef.current.click()}
        >
          Dosya Seç
        </button>
        {files.length > 0 && (
          <>
            <div style={{marginTop:6, fontSize:'0.98rem', color:'#333'}}>{files.map(f => f.name).join(', ')}</div>
            <button
              className="file-upload-analyze-btn"
              onClick={handleAnalyze}
              disabled={uploading}
              style={{marginTop:6}}
            >
              {uploading ? 'Yükleniyor...' : 'Analiz Et'}
            </button>
          </>
        )}
        {uploadMsg && <div className="file-upload-msg">{uploadMsg}</div>}
      </div>

      {/* Yeni: Dashboard ana grid düzeni */}
      <div style={{display:'flex',flexWrap:'wrap',gap:32,justifyContent:'center',alignItems:'flex-start',marginTop:32}}>
        {/* Sol sütun: kartlar ve grafikler */}
        <div style={{flex:'1 1 340px',maxWidth:420,minWidth:320,display:'flex',flexDirection:'column',gap:24}}>
          {/* Toplam Kullanıcı Info Kartı */}
          <div className="glass-card" style={{padding:'18px 38px',fontWeight:600,letterSpacing:'-0.5px',fontSize:'1.2rem',display:'flex',alignItems:'center',gap:10}}>
            <span style={{color:'#007aff',fontSize:'2.1rem',fontWeight:700,marginRight:15}}>{totalUsers}</span>
            <span>Toplam Kullanıcı</span>
          </div>
          {/* Segment Dağılımı Pasta Grafik */}
          <div className="glass-card" style={{padding:18,display:'flex',flexDirection:'column',alignItems:'center'}}>
            <div style={{fontWeight:600,marginBottom:10,fontSize:'1.14rem',letterSpacing:'-0.5px'}}>Segment Dağılımı</div>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={70}
                  dataKey="value"
                  nameKey="name"
                  isAnimationActive={true}
                >
                  {pieData.map((entry, idx) => (
                    <Cell key={`cell-${idx}`} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={v=>`${v} kullanıcı`} />
                <Legend verticalAlign="bottom" height={36} iconType="circle"/>
              </PieChart>
            </ResponsiveContainer>
          </div>
          {/* Ortalama Prediction Bar Chart */}
          <div className="glass-card" style={{padding:18,display:'flex',flexDirection:'column',alignItems:'center'}}>
            <div style={{fontWeight:600,marginBottom:10,fontSize:'1.14rem',letterSpacing:'-0.5px'}}>Segmentlere Göre Ortalama Tahmin</div>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={barData} margin={{top:12,right:24,left:0,bottom:12}}>
                <XAxis dataKey="segment" tick={{fontSize:13}} axisLine={false} tickLine={false} />
                <YAxis domain={[0,1]} tickFormatter={v=>v.toFixed(2)} axisLine={false} tickLine={false} />
                <Tooltip formatter={v=>Number(v).toFixed(2)} />
                <Bar dataKey="avgPrediction" fill="#6EC6FF" radius={[8,8,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        {/* Sağ sütun: arama ve tablo */}
        <div style={{flex:'2 1 500px',minWidth:340,maxWidth:800,display:'flex',flexDirection:'column',gap:18}}>
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',gap:10,marginBottom:18}}>
            <input
              className="search-input"
              type="text"
              placeholder="Ara: Kullanıcı, Segment, Tahmin..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{flex:1,minHeight:44,margin:0}}
            />
            <button
              className="file-upload-analyze-btn"
              style={{height:44,minHeight:44,margin:0,padding:'0 22px',fontWeight:600,fontSize:'1rem',borderRadius:12,boxShadow:'0 1.5px 6px 0 rgba(0,0,0,0.02)',background:'linear-gradient(90deg, #007aff 60%, #6ec6ff 100%)',display:'flex',alignItems:'center'}}
              onClick={() => {
                // CSV olarak indir fonksiyonu
                const headers = ['User ID','Segment','Prediction','Upsell Potential','Created At'];
                const rows = filteredSegments.map(seg => [
                  seg.user_id,
                  seg.segment,
                  Number(seg.prediction).toFixed(2),
                  seg.target_upselling_potential !== undefined ? (seg.target_upselling_potential ? 'Yes' : 'No') : '-',
                  new Date(seg.created_at).toLocaleString('tr-TR')
                ]);
                const csvContent = [headers, ...rows].map(row => row.map(val => `"${String(val).replace(/"/g,'""')}"`).join(',')).join('\n');
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', 'analiz_sonuclari.csv');
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
              }}
            >
              CSV İndir
            </button>
          </div>
          <table className="dashboard-table">
            <thead>
              <tr>
                <th>User ID</th>
                <th>Segment</th>
                <th>Prediction</th>
                <th>Upsell Potential</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {filteredSegments.map(seg => (
                <tr key={seg.id}>
                  <td>{seg.user_id}</td>
                  <td>{seg.segment}</td>
                  <td>{Number(seg.prediction).toFixed(2)}</td>
                  <td>{seg.target_upselling_potential !== undefined ? (seg.target_upselling_potential ? 'Yes' : 'No') : '-'}</td>
                  <td>{new Date(seg.created_at).toLocaleString('tr-TR')}</td>
                </tr>
              ))}
              {filteredSegments.length === 0 && (
                <tr><td colSpan={5} style={{textAlign:'center',color:'#bbb'}}>Sonuç bulunamadı</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
export default App;
