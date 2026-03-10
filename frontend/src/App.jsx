import React, { useState } from 'react';
import axios from 'axios';
import { Upload, FileAudio, CheckCircle, Loader2, ListTodo } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(''); // 'Transcribing', 'Analyzing', 'Syncing'
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setStatus('음성 파일을 전송 중입니다...');
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Simulate/Handle dynamic status updates if backend supported SSE, 
      // but for now we follow the linear async call.
      const response = await axios.post(`${API_BASE_URL}/upload`, formData);
      setResult(response.data);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('업로드 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
      setStatus('');
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-8">
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
          지능형 회의록 분석 에이전트
        </h1>
        <p className="text-slate-400">음성 파일을 업로드하면 AI가 분석하여 노션 칸반 보드에 업무를 자동 할당합니다.</p>
      </header>

      {/* Upload Section */}
      <div className="glass p-8 mb-8 text-center animate-in fade-in slide-in-from-bottom-4 duration-700">
        <label className="cursor-pointer block">
          <div className="border-2 border-dashed border-white/20 rounded-xl py-12 hover:border-primary/50 transition-colors">
            <Upload className="mx-auto mb-4 text-primary" size={48} />
            <p className="text-lg mb-2">{file ? file.name : "회의 음성 파일(mp3, wav)을 선택하거나 드래그하세요."}</p>
            <input type="file" className="hidden" accept="audio/*" onChange={handleFileChange} />
          </div>
        </label>
        
        <button 
          onClick={handleUpload}
          disabled={!file || loading}
          className={`mt-6 px-10 py-3 rounded-full font-semibold transition-all shadow-lg shadow-primary/20 ${
            !file || loading ? 'bg-slate-700 cursor-not-allowed' : 'bg-primary hover:bg-primary/80 active:scale-95'
          }`}
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <Loader2 className="animate-spin" /> {status}
            </span>
          ) : "분석 시작하기"}
        </button>
      </div>

      {/* Result Section */}
      {result && (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200">
          <div className="glass p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <CheckCircle className="text-green-400" /> 추출된 업무 (Notion 동기화 완료)
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.tasks.map((task, i) => (
                <div key={i} className="bg-white/5 border border-white/10 p-4 rounded-xl flex items-start gap-3">
                  <ListTodo className="text-secondary shrink-0" size={20} />
                  <div>
                    <h3 className="font-semibold text-slate-100">{task.title}</h3>
                    <p className="text-sm text-slate-400">담당자: {task.assignee} | 마감일: {task.deadline}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="glass p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <FileAudio className="text-primary" /> 회의록 원문
            </h2>
            <div className="bg-white/5 p-4 rounded-xl max-h-64 overflow-y-auto text-slate-300 whitespace-pre-wrap leading-relaxed">
              {result.raw_text}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
