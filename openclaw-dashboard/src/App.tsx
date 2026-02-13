import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Clock, Pause, Activity, 
  Terminal, RefreshCw, Brain,
  Database, Gauge, Rocket, FolderOpen
} from 'lucide-react';
import Editor from '@monaco-editor/react';
import { format } from 'date-fns';

interface CronJob {
  id: string;
  name: string;
  enabled: boolean;
  schedule: { expr?: string; everyMs?: number; kind: string };
  state: { nextRunAtMs: number; lastRunAtMs: number; lastStatus: string; lastDurationMs?: number };
  sessionTarget: string;
}

interface Session {
  sessionKey: string;
  activeMinutes?: number;
  createdAt?: number;
  lastMessage?: string;
  model?: string;
  kind?: string;
}

interface PlaybookFile {
  name: string;
  path: string;
  content: string;
}

// API base URL - use local JSON files for demo (gateway serves UI, not API)

async function fetchCronJobs(): Promise<CronJob[]> {
  try {
    const result = await fetch('/api/cron.json');
    if (result.ok) {
      const data = await result.json();
      return data.jobs || [];
    }
  } catch (e) {
    console.error('Failed to fetch cron jobs:', e);
  }
  return [];
}

async function fetchSessions(): Promise<Session[]> {
  try {
    const result = await fetch('/api/sessions.json');
    if (result.ok) {
      const data = await result.json();
      return data.sessions || [];
    }
  } catch (e) {
    console.error('Failed to fetch sessions:', e);
  }
  return [];
}

function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'cron' | 'playbook' | 'sessions' | 'research'>('overview');
  const [cronJobs, setCronJobs] = useState<CronJob[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [playbookFiles, setPlaybookFiles] = useState<PlaybookFile[]>([]);
  const [selectedPlaybook, setSelectedPlaybook] = useState<string | null>(null);
  const [playbookContent, setPlaybookContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [researchFiles, setResearchFiles] = useState<PlaybookFile[]>([]);
  const [selectedResearch, setSelectedResearch] = useState<string | null>(null);
  const [researchContent, setResearchContent] = useState<string>('');

  const loadData = useCallback(async () => {
    setRefreshing(true);
    setError(null);
    try {
      const [jobs, sess] = await Promise.all([fetchCronJobs(), fetchSessions()]);
      setCronJobs(jobs);
      setSessions(sess);

      // Load playbook files
      const playbookDir = '/api';
      const playbookNames = ['01_issue_management.md', '02_cron_jobs_definitions.md', '03_communication_channels.md', '04_api_configurations.md', '05_memory_system.md'];
      const pFiles: PlaybookFile[] = [];
      for (const name of playbookNames) {
        try {
          const response = await fetch(`${playbookDir}/${name}`);
          const content = await response.text();
          pFiles.push({ name, path: `${playbookDir}/${name}`, content });
        } catch (e) {
          pFiles.push({ name, path: `${playbookDir}/${name}`, content: '# Error loading file' });
        }
      }
      setPlaybookFiles(pFiles);
      if (pFiles.length > 0 && !selectedPlaybook) {
        setSelectedPlaybook(pFiles[0].name);
        setPlaybookContent(pFiles[0].content);
      }

      // Load research files
      const researchDir = '/api/research';
      const rFiles: PlaybookFile[] = [];
      try {
        const response = await fetch(`${researchDir}/README.md`);
        if (response.ok) {
          rFiles.push({ name: 'README.md', path: `${researchDir}/README.md`, content: await response.text() });
        }
      } catch (e) {
        rFiles.push({ name: 'README.md', path: `${researchDir}/README.md`, content: '# Research\n\nNo research files yet.' });
      }
      setResearchFiles(rFiles);
      if (rFiles.length > 0 && !selectedResearch) {
        setSelectedResearch(rFiles[0].name);
        setResearchContent(rFiles[0].content);
      }
    } catch (e) {
      setError('Failed to connect to API. Make sure you\'re on the same network or VPN.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [selectedPlaybook, selectedResearch]);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 15000);
    return () => clearInterval(interval);
  }, [loadData]);

  const activeJobs = cronJobs.filter(j => j.enabled);
  const upcomingJobs = cronJobs
    .filter(j => j.state?.nextRunAtMs)
    .sort((a, b) => (a.state?.nextRunAtMs || 0) - (b.state?.nextRunAtMs || 0))
    .slice(0, 4);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Gauge },
    { id: 'cron', label: 'Cron', icon: Clock },
    { id: 'playbook', label: 'Playbook', icon: Database },
    { id: 'sessions', label: 'Sessions', icon: Brain },
    { id: 'research', label: 'Research', icon: FolderOpen },
  ];

  return (
    <div className="min-h-screen bg-[#030308] text-white font-sans overflow-x-hidden">
      {/* Animated background with enhanced gradients */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[50%] -left-[50%] w-[200%] h-[200%] bg-[radial-gradient(ellipse_at_center,_rgba(139,92,246,0.2)_0%,_transparent_60%)]" />
        <div className="absolute top-[20%] right-[10%] w-[600px] h-[600px] bg-[radial_gradient(circle,_rgba(6,182,212,0.15)_0%,_transparent_60%)]" />
        <div className="absolute bottom-[10%] left-[20%] w-[400px] h-[400px] bg-[radial_gradient(circle,_rgba(236,72,153,0.12)_0%,_transparent_60%)]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[radial_gradient(circle,_rgba(99,102,241,0.08)_0%,_transparent_50%)]" />
        {/* Noise texture overlay */}
        <div className="absolute inset-0 opacity-[0.015]" style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")` }} />
      </div>

      {/* Glassmorphic Header */}
      <header className="relative z-10 border-b border-white/10 bg-[#030308]/60 backdrop-blur-2xl px-4 py-3">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/30">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 rounded-full border-2 border-[#030308]" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">
                <span className="bg-gradient-to-r from-white via-violet-200 to-violet-400 bg-clip-text text-transparent">
                  OpenClaw
                </span>
              </h1>
              <p className="text-[10px] text-violet-400/70 font-medium tracking-[0.2em] uppercase">Control Center</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="text-xs font-medium text-emerald-400">System Online</span>
            </div>
            <button 
              onClick={loadData}
              disabled={refreshing}
              className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all active:scale-95 hover:shadow-lg hover:shadow-violet-500/10"
            >
              <RefreshCw className={`w-4 h-4 text-violet-400 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </header>

      {/* Glassmorphic Navigation */}
      <nav className="relative z-10 border-b border-white/5 bg-[#030308]/30 backdrop-blur-xl overflow-x-auto">
        <div className="flex min-w-max px-4 max-w-7xl mx-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`relative px-5 py-4 text-sm font-medium tracking-wide transition-all whitespace-nowrap group ${
                activeTab === tab.id 
                  ? 'text-white' 
                  : 'text-white/40 hover:text-white/80'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <tab.icon className={`w-4 h-4 transition-transform duration-300 ${activeTab === tab.id ? '' : 'group-hover:scale-110'}`} />
                {tab.label}
              </div>
              {activeTab === tab.id && (
                <motion.div 
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-violet-500 via-purple-500 to-cyan-500"
                />
              )}
            </button>
          ))}
        </div>
      </nav>

      {/* Error Banner */}
      {error && (
        <div className="relative z-10 mx-4 mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
          <p className="text-xs text-red-400">{error}</p>
        </div>
      )}

      {/* Main Content */}
      <main className="relative z-10 p-4">
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div 
              initial={{ opacity: 0 }} 
              animate={{ opacity: 1 }}
              className="flex items-center justify-center h-[50vh]"
            >
              <div className="flex flex-col items-center gap-4">
                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center">
                  <Brain className="w-7 h-7 text-white animate-pulse" />
                </div>
                <p className="text-violet-400/60 text-sm">Loading...</p>
              </div>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              {activeTab === 'overview' && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <StatCard 
                    title="Agents" 
                    value={sessions.length.toString()}
                    subtitle="active"
                    icon={Brain}
                    gradient="from-violet-600 to-purple-600"
                  />
                  <StatCard 
                    title="Cron" 
                    value={activeJobs.length.toString()}
                    subtitle="enabled"
                    icon={Clock}
                    gradient="from-amber-500 to-orange-600"
                  />
                  <StatCard 
                    title="Playbook" 
                    value={playbookFiles.length.toString()}
                    subtitle="files"
                    icon={Database}
                    gradient="from-cyan-500 to-blue-600"
                  />
                  <StatCard 
                    title="Next" 
                    value={upcomingJobs[0]?.state?.nextRunAtMs ? format(new Date(upcomingJobs[0].state.nextRunAtMs), 'HH:mm') : '--:--'}
                    subtitle="scheduled"
                    icon={Rocket}
                    gradient="from-emerald-500 to-teal-600"
                  />

                  {/* Recent Activity */}
                  <div className="col-span-2 md:col-span-4">
                    <div className="rounded-2xl bg-gradient-to-br from-[#0a0a12] to-[#0d0d15] border border-white/8 p-5">
                      <div className="flex items-center gap-3 mb-4">
                        <Activity className="w-5 h-5 text-violet-400" />
                        <span className="text-base font-semibold text-white">Live Activity</span>
                      </div>
                      <div className="space-y-3">
                        {sessions.slice(0, 3).map((session) => (
                          <div key={session.sessionKey} className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                            <div className="flex items-center gap-3 min-w-0">
                              <Terminal className="w-5 h-5 text-violet-300 flex-shrink-0" />
                              <span className="text-sm text-white/80 truncate">{session.sessionKey.split(':').slice(-2).join(':')}</span>
                            </div>
                            <div className="flex items-center gap-3 flex-shrink-0">
                              <span className="text-sm text-white/50">{session.activeMinutes || 0}m</span>
                              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                            </div>
                          </div>
                        ))}
                        {sessions.length === 0 && (
                          <p className="text-sm text-white/30 text-center py-3">No active sessions</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'cron' && (
                <div className="space-y-4">
                  {cronJobs.map((job) => (
                    <div key={job.id} className="rounded-2xl bg-gradient-to-br from-[#0a0a12] to-[#0d0d15] border border-white/8 p-5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 min-w-0">
                          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${job.enabled ? 'bg-gradient-to-br from-violet-600 to-purple-600' : 'bg-white/5'}`}>
                            {job.enabled ? <Clock className="w-6 h-6 text-white" /> : <Pause className="w-6 h-6 text-white/30" />}
                          </div>
                          <div className="min-w-0">
                            <p className="text-base font-semibold text-white truncate">{job.name}</p>
                            <p className="text-sm text-white/50">{job.schedule.expr || `Every ${(job.schedule.everyMs || 0) / 1000}s`}</p>
                          </div>
                        </div>
                        <div className="text-right flex-shrink-0 ml-4">
                          <p className="text-xs text-white/40 uppercase tracking-wider">Next</p>
                          <p className="text-lg font-semibold text-white">
                            {job.state?.nextRunAtMs ? format(new Date(job.state.nextRunAtMs), 'MMM d, HH:mm') : 'N/A'}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'sessions' && (
                <div className="space-y-4">
                  {sessions.map((session) => (
                    <div key={session.sessionKey} className="rounded-2xl bg-gradient-to-br from-[#0a0a12] to-[#0d0d15] border border-white/8 p-5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 min-w-0">
                          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-600 to-blue-600 flex items-center justify-center">
                            <Brain className="w-6 h-6 text-white" />
                          </div>
                          <div className="min-w-0">
                            <p className="text-base font-semibold text-white truncate">{session.sessionKey}</p>
                            <p className="text-sm text-white/50">{session.model || 'minimax2.5'}</p>
                          </div>
                        </div>
                        <div className="text-right flex-shrink-0 ml-4">
                          <p className="text-2xl font-bold text-white">{session.activeMinutes || 0}m</p>
                          <p className="text-sm text-emerald-400">active</p>
                        </div>
                      </div>
                    </div>
                  ))}
                  {sessions.length === 0 && (
                    <div className="text-center py-12">
                      <Brain className="w-16 h-16 mx-auto mb-4 text-white/20" />
                      <p className="text-lg text-white/40">No active sessions</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'playbook' && (
                <div className="flex gap-3 h-[calc(100vh-220px)]">
                  <div className="w-24 md:w-48 flex-shrink-0 rounded-xl bg-gradient-to-br from-[#0a0a12] to-[#0d0d15] border border-white/5 p-3 overflow-y-auto">
                    <div className="flex items-center gap-2 mb-2 text-xs text-cyan-400">
                      <Database className="w-3.5 h-3.5" />
                      <span className="font-medium">Knowledge</span>
                    </div>
                    <div className="space-y-1">
                      {playbookFiles.map(file => (
                        <button
                          key={file.name}
                          onClick={() => { setSelectedPlaybook(file.name); setPlaybookContent(file.content); }}
                          className={`w-full text-left px-2 py-1.5 rounded text-xs transition-all truncate ${
                            selectedPlaybook === file.name 
                              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30' 
                              : 'hover:bg-white/5 text-white/60 hover:text-white/90'
                          }`}
                        >
                          {file.name.replace('.md', '').replace(/^\d+_/, '')}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="flex-1 rounded-xl bg-[#0a0a12] border border-white/5 overflow-hidden">
                    <Editor
                      height="100%"
                      defaultLanguage="markdown"
                      value={playbookContent}
                      onChange={(value) => setPlaybookContent(value || '')}
                      theme="vs-dark"
                      options={{
                        minimap: { enabled: false },
                        fontSize: 13,
                        lineNumbers: 'on',
                        wordWrap: 'on',
                        scrollBeyondLastLine: false,
                        padding: { top: 16, bottom: 16 },
                        fontFamily: 'JetBrains Mono, monospace',
                      }}
                    />
                  </div>
                </div>
              )}

              {activeTab === 'research' && (
                <div className="flex gap-3 h-[calc(100vh-220px)]">
                  <div className="w-24 md:w-48 flex-shrink-0 rounded-xl bg-gradient-to-br from-[#0a0a12] to-[#0d0d15] border border-white/5 p-3 overflow-y-auto">
                    <div className="flex items-center gap-2 mb-2 text-xs text-amber-400">
                      <FolderOpen className="w-3.5 h-3.5" />
                      <span className="font-medium">Research</span>
                    </div>
                    <div className="space-y-1">
                      {researchFiles.map(file => (
                        <button
                          key={file.name}
                          onClick={() => { setSelectedResearch(file.name); setResearchContent(file.content); }}
                          className={`w-full text-left px-2 py-1.5 rounded text-xs transition-all truncate ${
                            selectedResearch === file.name 
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' 
                              : 'hover:bg-white/5 text-white/60 hover:text-white/90'
                          }`}
                        >
                          {file.name.replace('.md', '')}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="flex-1 rounded-xl bg-[#0a0a12] border border-white/5 overflow-hidden">
                    <Editor
                      height="100%"
                      defaultLanguage="markdown"
                      value={researchContent}
                      onChange={(value) => setResearchContent(value || '')}
                      theme="vs-dark"
                      options={{
                        minimap: { enabled: false },
                        fontSize: 13,
                        lineNumbers: 'on',
                        wordWrap: 'on',
                        scrollBeyondLastLine: false,
                        padding: { top: 16, bottom: 16 },
                        fontFamily: 'JetBrains Mono, monospace',
                      }}
                    />
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

function StatCard({ title, value, subtitle, icon: Icon, gradient }: { 
  title: string; 
  value: string; 
  subtitle: string;
  icon: any; 
  gradient: string;
}) {
  return (
    <motion.div 
      whileHover={{ scale: 1.02, y: -2 }}
      className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#0a0a12] via-[#0d0d15] to-[#0a0a12] border border-white/8 p-5 group hover:border-white/15 transition-colors"
    >
      {/* Glow effect */}
      <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-500`} />
      <div className={`absolute -top-12 -right-12 w-24 h-24 bg-gradient-to-br ${gradient} opacity-20 blur-3xl group-hover:opacity-30 transition-opacity`} />
      
      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
          <span className="text-xs text-white/40 uppercase tracking-widest font-medium">{subtitle}</span>
        </div>
        <p className="text-5xl font-bold text-white tracking-tight">{value}</p>
        <p className="text-sm text-white/60 mt-2 font-medium">{title}</p>
      </div>
    </motion.div>
  );
}

export default App;
