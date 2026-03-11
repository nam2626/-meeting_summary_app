import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, FileAudio, CheckCircle, Loader2, ListTodo, RefreshCw, Send, Clock, ChevronDown, ChevronUp } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

function TaskCard({ task }) {
  return (
    <div className="bg-white/5 border border-white/10 p-4 rounded-xl flex items-start gap-3">
      <ListTodo className="text-secondary shrink-0" size={20} />
      <div>
        <h3 className="font-semibold text-slate-100">{task.title}</h3>
        <p className="text-sm text-slate-400">담당자: {task.assignee} | 마감일: {task.deadline}</p>
      </div>
    </div>
  );
}

function EditPanel({ rawText, meetingId, originalText, onRestore }) {
  const [editableText, setEditableText] = useState(rawText);
  const [notionLoading, setNotionLoading] = useState(false);
  const [notionResult, setNotionResult] = useState(null);

  const handleRegisterToNotion = async () => {
    if (!editableText.trim()) return;
    setNotionLoading(true);
    setNotionResult(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/analyze`, {
        text: editableText,
        meeting_id: meetingId ?? null,
      });
      setNotionResult(response.data.tasks);
    } catch (error) {
      console.error('Notion 등록 실패:', error);
      alert('Notion 등록 중 오류가 발생했습니다.');
    } finally {
      setNotionLoading(false);
    }
  };

  return (
    <div className="mt-4 space-y-4">
      <textarea
        className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-slate-300 leading-relaxed resize-y min-h-36 focus:outline-none focus:border-primary/50 transition-colors text-sm"
        value={editableText}
        onChange={(e) => setEditableText(e.target.value)}
      />
      <div className="flex gap-3 justify-end">
        <button
          onClick={() => setEditableText(originalText)}
          className="flex items-center gap-2 px-5 py-2 rounded-full text-sm bg-white/10 hover:bg-white/20 transition-colors"
        >
          <RefreshCw size={14} /> 원문 복원
        </button>
        <button
          onClick={handleRegisterToNotion}
          disabled={notionLoading}
          className={`flex items-center gap-2 px-6 py-2 rounded-full font-semibold text-sm transition-all ${
            notionLoading ? 'bg-slate-700 cursor-not-allowed' : 'bg-secondary hover:bg-secondary/80 active:scale-95 shadow-lg shadow-secondary/20'
          }`}
        >
          {notionLoading ? (
            <><Loader2 className="animate-spin" size={14} /> Notion 등록 중...</>
          ) : (
            <><Send size={14} /> Notion에 등록하기</>
          )}
        </button>
      </div>
      {notionResult && (
        <div className="glass p-4 mt-2">
          <h3 className="font-bold mb-3 flex items-center gap-2 text-green-400">
            <CheckCircle size={16} /> Notion 등록 완료
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {notionResult.map((task, i) => <TaskCard key={i} task={task} />)}
          </div>
        </div>
      )}
    </div>
  );
}

function MeetingHistoryItem({ meeting }) {
  const [open, setOpen] = useState(false);
  const dateStr = meeting.created_at
    ? new Date(meeting.created_at).toLocaleString('ko-KR')
    : '';

  return (
    <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(v => !v)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-white/5 transition-colors text-left"
      >
        <div>
          <p className="font-semibold text-slate-100">{meeting.title}</p>
          <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-1">
            <Clock size={11} /> {dateStr}
          </p>
        </div>
        {open ? <ChevronUp size={18} className="text-slate-400 shrink-0" /> : <ChevronDown size={18} className="text-slate-400 shrink-0" />}
      </button>
      {open && (
        <div className="px-5 pb-5 border-t border-white/10">
          <EditPanel
            rawText={meeting.raw_text}
            meetingId={meeting.id}
            originalText={meeting.raw_text}
          />
        </div>
      )}
    </div>
  );
}

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [result, setResult] = useState(null);
  const [meetings, setMeetings] = useState([]);

  const fetchMeetings = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/meetings`);
      setMeetings(res.data);
    } catch (e) {
      console.error('회의록 목록 불러오기 실패:', e);
    }
  };

  useEffect(() => {
    fetchMeetings();
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setStatus('음성 변환(STT) 중입니다...');
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData);
      setResult(response.data);
      fetchMeetings(); // 목록 갱신
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
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
          지능형 회의록 분석 에이전트
        </h1>
        <p className="text-slate-400">음성 파일을 업로드하면 AI가 분석하여 노션 칸반 보드에 업무를 자동 할당합니다.</p>
      </header>

      {/* Upload Section */}
      <div className="glass p-8 mb-8 text-center">
        <label className="cursor-pointer block">
          <div className="border-2 border-dashed border-white/20 rounded-xl py-10 hover:border-primary/50 transition-colors">
            <Upload className="mx-auto mb-4 text-primary" size={42} />
            <p className="text-lg mb-2">{file ? file.name : "회의 음성 파일(mp3, wav)을 선택하거나 드래그하세요."}</p>
            <input type="file" className="hidden" accept="audio/*" onChange={handleFileChange} />
          </div>
        </label>
        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className={`mt-5 px-10 py-3 rounded-full font-semibold transition-all shadow-lg shadow-primary/20 ${
            !file || loading ? 'bg-slate-700 cursor-not-allowed' : 'bg-primary hover:bg-primary/80 active:scale-95'
          }`}
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <Loader2 className="animate-spin" /> {status}
            </span>
          ) : "STT 변환 시작"}
        </button>
      </div>

      {/* 방금 업로드한 결과 */}
      {result && (
        <div className="glass p-6 mb-8">
          <h2 className="text-xl font-bold mb-1 flex items-center gap-2">
            <FileAudio className="text-primary" /> 방금 변환된 회의록
          </h2>
          <p className="text-xs text-slate-400 mb-4">원문을 수정한 후 Notion에 등록할 수 있습니다.</p>
          <EditPanel
            rawText={result.raw_text}
            meetingId={result.meeting_id}
            originalText={result.raw_text}
          />
        </div>
      )}

      {/* 기존 회의록 목록 */}
      <div className="glass p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Clock className="text-secondary" /> 기존 회의록
          </h2>
          <button
            onClick={fetchMeetings}
            className="flex items-center gap-1 text-sm text-slate-400 hover:text-slate-200 transition-colors"
          >
            <RefreshCw size={14} /> 새로고침
          </button>
        </div>
        {meetings.length === 0 ? (
          <p className="text-slate-500 text-sm text-center py-6">저장된 회의록이 없습니다.</p>
        ) : (
          <div className="space-y-3">
            {meetings.map((m) => <MeetingHistoryItem key={m.id} meeting={m} />)}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
