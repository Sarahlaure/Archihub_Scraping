'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Header } from "@/components/ui/header-1";
import { Button } from "@/components/ui/button";
import {
  BookmarkIcon,
  ExternalLinkIcon,
  RefreshCwIcon,
  MapPinIcon,
  CalendarIcon,
  BriefcaseIcon,
  NewspaperIcon,
  TrophyIcon,
  MoonIcon,
  SunIcon,
  ArchiveIcon,
  ArrowRightIcon,
  ClockIcon,
  FilterIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useTheme } from "next-themes";
import { differenceInDays, parseISO, isValid } from "date-fns";

interface ContentItem {
  title: string;
  link: string;
  description: string;
  type?: 'competition' | 'job' | 'news';
  deadline?: string;
  deadline_iso?: string | null;
  location?: string;
  salary?: string;
  date?: string;
}

type TabType = 'competitions' | 'jobs' | 'news' | 'saved' | 'archives';

export default function Home() {
  const [competitions, setCompetitions] = useState<ContentItem[]>([]);
  const [jobs, setJobs] = useState<ContentItem[]>([]);
  const [news, setNews] = useState<ContentItem[]>([]);
  const [savedItems, setSavedItems] = useState<ContentItem[]>([]);
  const [lastSyncedAt, setLastSyncedAt] = useState<string | null>(null);

  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('competitions');
  const [locationFilter, setLocationFilter] = useState<string>('all');
  const { theme, setTheme } = useTheme();

  // Load saved articles from local storage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem('saved_archicomp');
      if (saved) setSavedItems(JSON.parse(saved));
    } catch (e) {
      console.error("Failed to parse saved items", e);
    }
  }, []);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      // Add cache-busting parameter to force fresh data
      const ts = Date.now();
      const [compRes, jobsRes, newsRes] = await Promise.all([
        fetch(`/competitions.json?t=${ts}`),
        fetch(`/jobs.json?t=${ts}`),
        fetch(`/news.json?t=${ts}`),
      ]);

      if (compRes.ok) setCompetitions(await compRes.json());
      if (jobsRes.ok) setJobs(await jobsRes.json());
      if (newsRes.ok) setNews(await newsRes.json());

      setLastSyncedAt(new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }));
    } catch (err) {
      console.error("Failed to fetch data:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const isSaved = (link: string) => savedItems.some(i => i.link === link);

  const toggleSave = (item: ContentItem) => {
    let newSaved: ContentItem[];
    if (isSaved(item.link)) {
      newSaved = savedItems.filter(i => i.link !== item.link);
    } else {
      newSaved = [item, ...savedItems];
    }
    setSavedItems(newSaved);
    localStorage.setItem('saved_archicomp', JSON.stringify(newSaved));
  };

  // Client-side deduplication by normalized title
  const normalizeTitle = (title: string) => {
    return title
      .toLowerCase()
      .replace(/[\r\n]+/g, ' ')
      .replace(/\s+/g, ' ')
      .replace(/[^a-z0-9àâäéèêëïîôùûüÿçœæ ]/g, '')
      .trim();
  };

  const deduplicateByTitle = (items: ContentItem[]) => {
    const seen = new Map<string, ContentItem>();
    const result: ContentItem[] = [];
    for (const item of items) {
      const norm = normalizeTitle(item.title);
      if (norm.length < 5) continue;
      if (seen.has(norm)) {
        // Prefer items with known deadlines
        const existing = seen.get(norm)!;
        if (!existing.deadline_iso && item.deadline_iso) {
          const idx = result.indexOf(existing);
          if (idx >= 0) result[idx] = item;
          seen.set(norm, item);
        }
      } else {
        seen.set(norm, item);
        result.push(item);
      }
    }
    return result;
  };

  const getDisplayedItems = () => {
    const today = new Date();

    const sortByDeadline = (a: ContentItem, b: ContentItem) => {
      if (a.deadline_iso && b.deadline_iso) {
        return new Date(a.deadline_iso).getTime() - new Date(b.deadline_iso).getTime();
      }
      // Items without deadline go last
      if (a.deadline_iso && !b.deadline_iso) return -1;
      if (!a.deadline_iso && b.deadline_iso) return 1;
      return 0;
    };

    if (activeTab === 'competitions') {
      const active = competitions.filter(item => {
        // Show items with valid future deadlines
        if (item.deadline_iso) {
          const d = parseISO(item.deadline_iso);
          return isValid(d) && differenceInDays(d, today) >= 0;
        }
        // ONLY SHOW items with known deadlines
        return false;
      }).sort(sortByDeadline);
      return deduplicateByTitle(active);
    }

    if (activeTab === 'archives') {
      // Concours expires (deadline passee) + concours sans date connue
      const expired = competitions.filter(item => {
        if (!item.deadline_iso) return true; // date inconnue -> archive par defaut
        const d = parseISO(item.deadline_iso);
        return isValid(d) && differenceInDays(d, today) < 0;
      }).sort((a, b) => {
        // Expires avec date d'abord (du plus recent au plus ancien), sans date ensuite
        if (a.deadline_iso && !b.deadline_iso) return -1;
        if (!a.deadline_iso && b.deadline_iso) return 1;
        return -sortByDeadline(a, b);
      });
      return deduplicateByTitle(expired);
    }

    if (activeTab === 'jobs') {
      if (locationFilter === 'all') return jobs;
      return jobs.filter(j => j.location?.toLowerCase().includes(locationFilter.toLowerCase()));
    }
    if (activeTab === 'news') return news;
    return savedItems;
  };

  const displayedItems = getDisplayedItems();

  // Count helpers for tabs
  const activeCompetitionsCount = deduplicateByTitle(competitions.filter(item => {
    if (item.deadline_iso) {
      const d = parseISO(item.deadline_iso);
      return isValid(d) && differenceInDays(d, new Date()) >= 0;
    }
    return false;
  })).length;

  // Tab definitions for bottom nav
  const tabs: { id: TabType; label: string; Icon: React.ElementType; count?: number }[] = [
    { id: 'competitions', label: 'Concours', Icon: TrophyIcon, count: !loading && activeCompetitionsCount > 0 ? activeCompetitionsCount : undefined },
    { id: 'jobs', label: 'Emplois', Icon: BriefcaseIcon, count: !loading && jobs.length > 0 ? jobs.length : undefined },
    { id: 'news', label: 'Actus', Icon: NewspaperIcon, count: !loading && news.length > 0 ? news.length : undefined },
    { id: 'saved', label: 'Favoris', Icon: BookmarkIcon, count: savedItems.length > 0 ? savedItems.length : undefined },
    { id: 'archives', label: 'Archives', Icon: ArchiveIcon },
  ];

  return (
    <div className="relative flex min-h-screen flex-col font-inter bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-50 transition-colors selection:bg-indigo-500/20">

      {/* Premium Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] rounded-full bg-indigo-500/10 dark:bg-indigo-500/5 blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] rounded-full bg-amber-500/5 dark:bg-rose-500/5 blur-[120px]" />
        <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))] dark:opacity-20 opacity-30" />
      </div>

      <Header />

      {/* ── MOBILE BOTTOM NAVIGATION BAR ── */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white/95 dark:bg-slate-900/95 backdrop-blur-lg border-t border-slate-200 dark:border-slate-800 safe-area-pb">
        <div className="flex items-stretch justify-around px-1">
          {tabs.map(({ id, label, Icon, count }) => (
            <button
              key={id}
              onClick={() => {
                setActiveTab(id);
                document.getElementById('hub-content')?.scrollIntoView({ behavior: 'smooth' });
              }}
              className={cn(
                "flex flex-col items-center justify-center gap-1 py-3 px-2 flex-1 relative transition-all duration-200",
                activeTab === id
                  ? "text-[#a68a30] dark:text-[#c2a65a]"
                  : "text-slate-400 dark:text-slate-500"
              )}
            >
              <div className="relative">
                <Icon className="w-5 h-5" />
                {count !== undefined && (
                  <span className={cn(
                    "absolute -top-1.5 -right-2 min-w-[16px] h-4 flex items-center justify-center px-1 text-[9px] font-bold rounded-full text-white",
                    activeTab === id ? "bg-[#a68a30] dark:bg-[#c2a65a]" : "bg-slate-400 dark:bg-slate-600"
                  )}>
                    {count > 99 ? '99+' : count}
                  </span>
                )}
              </div>
              <span className="text-[10px] font-semibold tracking-wide leading-none">{label}</span>
              {activeTab === id && (
                <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-6 h-0.5 rounded-full bg-[#a68a30] dark:bg-[#c2a65a]" />
              )}
            </button>
          ))}
        </div>
      </nav>

      <main className="flex-grow z-10 w-full pb-24 md:pb-16 px-4 sm:px-6 lg:px-8">

        {/* ── MOBILE HERO (compact) ── */}
        <section className="md:hidden w-full pt-5 pb-5 px-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="h-px w-8 bg-[#a68a30] dark:bg-[#c2a65a]"></div>
            <span className="text-[#a68a30] dark:text-[#c2a65a] uppercase font-bold tracking-[0.2em] text-xs">ARCHI SPACE</span>
          </div>
          <h1 className="text-3xl leading-tight text-slate-900 dark:text-white font-serif mb-2 tracking-tight">
            <span>Saisis </span>
            <span className="italic text-[#a68a30] dark:text-[#c2a65a] font-light">ta prochaine</span>
            <br />
            <span className="text-transparent [-webkit-text-stroke:1px_rgba(15,23,42,0.4)] dark:[-webkit-text-stroke:1px_rgba(255,255,255,0.4)]">opportunité.</span>
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 font-light mb-4 leading-relaxed">
            Concours, emplois &amp; actualités en architecture — mis à jour quotidiennement.
          </p>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              onClick={fetchData}
              disabled={loading}
              className="flex-1 rounded-none bg-[#a68a30] dark:bg-[#c2a65a] text-white dark:text-slate-950 hover:bg-[#8a7224] uppercase tracking-wider text-xs h-9"
            >
              <RefreshCwIcon className={cn("mr-1.5 size-3", loading && "animate-spin")} />
              Actualiser
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="rounded-none border-slate-300 dark:border-slate-800 bg-transparent h-9 w-9 p-0 flex-shrink-0"
            >
              <SunIcon className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <MoonIcon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            </Button>
          </div>
          {lastSyncedAt && (
            <p className="mt-2 flex items-center gap-1 text-[10px] text-slate-400 dark:text-slate-500">
              <ClockIcon className="w-2.5 h-2.5" /> Données chargées à {lastSyncedAt}
            </p>
          )}
        </section>

        {/* ── DESKTOP HERO (full) ── */}
        <section className="hidden md:flex relative w-full mx-auto max-w-7xl pt-8 pb-10 overflow-hidden rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm dark:shadow-none bg-white dark:bg-[#0a0a0d] mb-12 mt-4 px-8 lg:px-16 flex-col justify-center">

          {/* Controls Container */}
          <div className="absolute top-6 right-6 flex items-center gap-3 z-50">
            {lastSyncedAt && (
              <span className="hidden sm:flex items-center gap-1.5 text-xs text-slate-400 dark:text-slate-500 font-medium">
                <ClockIcon className="w-3 h-3" />
                Données chargées à {lastSyncedAt}
              </span>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={fetchData}
              disabled={loading}
              className="rounded-none border-slate-300 dark:border-slate-800 bg-transparent text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-900 uppercase tracking-widest text-xs h-10 px-4"
            >
              <RefreshCwIcon className={cn("mr-2 size-3", loading && "animate-spin")} />
              Actualiser
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="rounded-none border-slate-300 dark:border-slate-800 bg-transparent text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-900 h-10 w-10"
            >
              <SunIcon className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <MoonIcon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Toggle theme</span>
            </Button>
          </div>

          <div className="relative z-10 max-w-4xl pt-8 pb-12">
            <div className="flex items-center gap-4 mb-10">
              <div className="h-px w-12 bg-[#a68a30] dark:bg-[#c2a65a]"></div>
              <span className="text-[#a68a30] dark:text-[#c2a65a] uppercase font-bold tracking-[0.2em] text-sm">ARCHI SPACE</span>
            </div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl leading-[1] text-slate-900 dark:text-white font-serif mb-8 select-none tracking-tight">
              <span className="block">Saisis</span>
              <span className="block"><span className="italic text-[#a68a30] dark:text-[#c2a65a] pr-4 font-light">ta prochaine</span></span>
              <span className="block text-transparent [-webkit-text-stroke:1px_rgba(15,23,42,0.4)] dark:[-webkit-text-stroke:1px_rgba(255,255,255,0.4)]">opportunité.</span>
            </h1>

            <p className="max-w-xl text-lg md:text-xl text-slate-600 dark:text-slate-400 font-light mb-12">
              Découvre les concours, emplois et actualités qui peuvent <strong className="text-slate-900 dark:text-white font-medium">faire avancer ton parcours</strong>, mis à jour quotidiennement.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 max-w-2xl">
              <Button
                size="lg"
                className="rounded-none font-semibold px-8 py-7 bg-[#a68a30] dark:bg-[#c2a65a] text-white dark:text-slate-950 hover:bg-[#8a7224] dark:hover:bg-[#d8be72] transition-colors uppercase tracking-wider text-sm w-full sm:w-auto"
                onClick={() => { document.getElementById('hub-content')?.scrollIntoView({ behavior: 'smooth' }); setActiveTab('competitions'); }}
              >
                EXPLORER LES CONCOURS <ArrowRightIcon className="ml-4 w-4 h-4" />
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="rounded-none px-8 py-7 bg-transparent border border-slate-300 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors uppercase tracking-wider text-sm w-full sm:w-auto"
                onClick={() => { document.getElementById('hub-content')?.scrollIntoView({ behavior: 'smooth' }); setActiveTab('jobs'); }}
              >
                VOIR LES OFFRES D&apos;EMPLOI <ArrowRightIcon className="ml-4 w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* MASSIVE BACKGROUND TEXT */}
          <div className="absolute bottom-[-15%] xl:bottom-[-20%] left-0 right-0 overflow-hidden pointer-events-none select-none z-0 opacity-5 dark:opacity-10">
            <h2 className="text-[30vw] font-serif leading-none whitespace-nowrap text-slate-900 dark:text-white text-center tracking-tighter">ARCH</h2>
          </div>
        </section>

        {/* ── CONTENT SECTION ── */}
        <div id="hub-content" className="max-w-7xl px-0 sm:px-6 pb-12 mx-auto">

          {/* ── DESKTOP STICKY TABS (hidden on mobile, replaced by bottom nav) ── */}
          <div className="hidden md:flex sticky top-14 z-40 bg-slate-50/90 dark:bg-slate-950/90 backdrop-blur-md pt-4 pb-4 border-b border-slate-200 dark:border-slate-800 -mx-6 px-6 lg:-mx-8 lg:px-8 mb-10 flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex space-x-2 overflow-x-auto w-full md:w-auto hidescrollbar">
              {tabs.map(({ id, label, Icon, count }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id)}
                  className={cn(
                    "flex items-center gap-2 px-4 py-4 text-sm font-semibold tracking-wide transition-all duration-300 border-b-2 whitespace-nowrap",
                    activeTab === id ? "border-[#a68a30] dark:border-[#c2a65a] text-slate-900 dark:text-white" : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
                  )}
                >
                  <Icon className="w-4 h-4" /> {label}
                  {count !== undefined && (
                    <span className={cn("flex items-center justify-center px-2 py-0.5 ml-1 text-xs text-white rounded-full", activeTab === id ? "bg-[#a68a30] dark:bg-[#c2a65a]" : "bg-slate-300 dark:bg-slate-700")}>
                      {count}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* ── MOBILE: Section title for active tab ── */}
          <div className="md:hidden mb-5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              {(() => { const t = tabs.find(t => t.id === activeTab); return t ? <t.Icon className="w-5 h-5 text-[#a68a30] dark:text-[#c2a65a]" /> : null; })()}
              <h2 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
                {tabs.find(t => t.id === activeTab)?.label}
              </h2>
              {(() => { const t = tabs.find(t => t.id === activeTab); return t?.count !== undefined ? (
                <span className="bg-[#a68a30] dark:bg-[#c2a65a] text-white dark:text-slate-950 text-xs font-bold px-2 py-0.5 rounded-full">{t.count}</span>
              ) : null; })()}
            </div>
          </div>

          {/* Location filter bar for jobs */}
          {activeTab === 'jobs' && jobs.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap mb-6 mt-2">
              <FilterIcon className="w-4 h-4 text-slate-400 dark:text-slate-500 flex-shrink-0" />
              <button
                onClick={() => setLocationFilter('all')}
                className={cn(
                  "px-3 py-1.5 text-xs font-bold tracking-wider uppercase rounded-full border transition-all duration-200",
                  locationFilter === 'all'
                    ? "bg-[#a68a30] dark:bg-[#c2a65a] text-white dark:text-slate-950 border-transparent"
                    : "bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-[#a68a30] dark:hover:border-[#c2a65a]"
                )}
              >
                Toutes ({jobs.length})
              </button>
              {Array.from(new Set(jobs.map(j => j.location).filter(Boolean))).sort().map(loc => {
                const count = jobs.filter(j => j.location === loc).length;
                return (
                  <button
                    key={loc}
                    onClick={() => setLocationFilter(loc === locationFilter ? 'all' : loc!)}
                    className={cn(
                      "px-3 py-1.5 text-xs font-bold tracking-wider uppercase rounded-full border transition-all duration-200 flex items-center gap-1",
                      locationFilter === loc
                        ? "bg-[#a68a30] dark:bg-[#c2a65a] text-white dark:text-slate-950 border-transparent"
                        : "bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-[#a68a30] dark:hover:border-[#c2a65a]"
                    )}
                  >
                    <MapPinIcon className="w-3 h-3" />
                    {loc}
                    <span className="opacity-60">({count})</span>
                  </button>
                );
              })}
            </div>
          )}

          {/* Cards Grid */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 md:gap-8">
              {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
                <div key={i} className="h-[280px] md:h-[320px] rounded-[1.5rem] md:rounded-[2rem] bg-slate-200/50 dark:bg-slate-800/50 animate-pulse border border-slate-200 dark:border-slate-800 shadow-sm" />
              ))}
            </div>
          ) : displayedItems.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 md:gap-8">
              {displayedItems.map((item, i) => {
                const isItemSaved = isSaved(item.link);
                const TypeIcon = item.type === 'competition' ? TrophyIcon : item.type === 'job' ? BriefcaseIcon : NewspaperIcon;

                // Highlight ending soon for competitions
                const daysLeft = item.deadline_iso && isValid(parseISO(item.deadline_iso))
                  ? differenceInDays(parseISO(item.deadline_iso), new Date())
                  : null;
                const isEndingSoon = item.type === 'competition' && activeTab === 'competitions' && daysLeft !== null && daysLeft <= 14;
                const hasNoDeadline = item.type === 'competition' && !item.deadline_iso;

                return (
                  <div
                    key={`${item.link}-${i}`}
                    className={cn(
                      "group relative flex flex-col h-full gap-4 p-5 md:p-7 transition-all duration-500 border shadow-md bg-white dark:bg-slate-900 rounded-[1.5rem] md:rounded-[2rem] active:scale-[0.98] md:hover:shadow-xl md:hover:-translate-y-2",
                      "border-slate-200 dark:border-slate-800",
                      isEndingSoon && "ring-2 ring-rose-500/50 border-rose-500/50"
                    )}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex flex-col gap-2 flex-grow">
                        <span className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold tracking-wider uppercase rounded-full w-fit bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                          <TypeIcon className="w-3.5 h-3.5" />
                          {item.type === 'competition' ? 'Concours' : item.type === 'job' ? 'Emploi' : item.type === 'news' ? 'Actualité' : 'Article'}
                        </span>

                        {/* Meta information tags */}
                        {item.type === 'competition' && item.deadline && !hasNoDeadline && (
                          <span className={cn(
                            "flex items-center gap-1.5 text-xs font-bold",
                            activeTab === 'archives' ? "text-slate-500" : isEndingSoon ? "text-rose-500" : "text-emerald-600 dark:text-emerald-400"
                          )}>
                            <CalendarIcon className="w-3.5 h-3.5" />
                            {activeTab === 'archives' ? (item.deadline && item.deadline !== 'Unknown' ? `Clôturé le ${item.deadline}` : 'Clôturé') : item.deadline}
                            {daysLeft !== null && daysLeft <= 14 && activeTab === 'competitions' && (
                              <span className="ml-1 px-1.5 py-0.5 rounded bg-rose-100 dark:bg-rose-950 text-rose-600 dark:text-rose-400 text-[10px]">
                                J-{daysLeft}
                              </span>
                            )}
                          </span>
                        )}

                        {hasNoDeadline && (activeTab === 'competitions' || activeTab === 'archives') && (
                          <span className="flex items-center gap-1.5 text-xs font-medium text-slate-400 dark:text-slate-500">
                            <CalendarIcon className="w-3.5 h-3.5" />
                            {activeTab === 'archives' ? 'Date de clôture inconnue' : 'Date inconnue'}
                          </span>
                        )}

                        {item.type === 'job' && item.location && (
                          <span className="flex items-center gap-1.5 text-xs font-bold text-indigo-600 dark:text-indigo-400">
                            <MapPinIcon className="w-3.5 h-3.5" /> {item.location}
                          </span>
                        )}

                        {item.type === 'news' && item.date && item.date !== 'Recent' && (
                          <span className="flex items-center gap-1.5 text-xs font-medium text-slate-500 dark:text-slate-400">
                            <CalendarIcon className="w-3.5 h-3.5" /> {item.date}
                          </span>
                        )}
                      </div>

                      <button
                        onClick={() => toggleSave(item)}
                        className={cn(
                          "rounded-full p-3 transition-colors shadow-sm border flex-shrink-0",
                          isItemSaved
                            ? "text-[#a68a30] bg-[#a68a30]/10 border-[#a68a30]/20 dark:text-[#c2a65a] dark:bg-[#c2a65a]/10 dark:border-[#c2a65a]/20"
                            : "text-slate-400 bg-white dark:bg-slate-800 border-slate-100 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700",
                        )}
                        title={isItemSaved ? "Retirer des favoris" : "Ajouter aux favoris"}
                      >
                        <BookmarkIcon className={cn("size-4", isItemSaved && "fill-current")} />
                      </button>
                    </div>

                    <h3 className="text-xl font-extrabold font-outfit leading-tight text-slate-800 dark:text-slate-100 group-hover:text-[#a68a30] dark:group-hover:text-[#c2a65a] transition-colors line-clamp-3">
                      {item.title}
                    </h3>

                    <p className="text-sm font-medium leading-relaxed text-slate-500 dark:text-slate-400 line-clamp-3 flex-grow pb-4">
                      {(() => {
                        let desc = item.description || "";
                        if (item.type === 'competition' && (desc.length < 35 || desc.includes('Bustler') || desc.includes('competitions.archi'))) {
                          return "Découvrez cette opportunité d'architecture. Consultez la page officielle pour accéder au brief détaillé, aux critères du jury et aux récompenses proposées.";
                        }
                        if (item.type === 'job' && desc.length < 35) {
                          return "Nouvelle offre d'emploi en architecture. Cliquez pour voir les exigences du poste et postuler directement auprès de l'agence.";
                        }
                        if (desc.length < 15) {
                          return "Consultez le site officiel pour plus de détails sur cet élément.";
                        }
                        return desc;
                      })()}
                    </p>

                    <div className="pt-5 mt-auto border-t border-slate-100 dark:border-slate-800">
                      <a
                        href={item.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex w-full items-center justify-center gap-2 py-2.5 px-4 text-sm font-bold tracking-wide text-slate-900 bg-slate-100 hover:bg-slate-200 dark:text-white dark:bg-slate-800 dark:hover:bg-slate-700 rounded-none transition-all uppercase"
                      >
                        {activeTab === 'archives' ? "Voir l\u2019archive" : activeTab === 'jobs' ? "Voir l\u2019offre" : activeTab === 'news' ? "Lire l\u2019article" : activeTab === 'saved' ? "Consulter" : "Voir le concours"} <ExternalLinkIcon className="size-4" />
                      </a>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center p-10 md:p-16 text-center rounded-[2rem] md:rounded-[3rem] bg-white/40 dark:bg-slate-900/40 backdrop-blur-md border border-slate-200 dark:border-slate-800 shadow-inner min-h-[300px] md:min-h-[400px]">
              <div className="p-5 md:p-6 mb-5 md:mb-8 rounded-full bg-slate-100 dark:bg-slate-800 shadow-sm">
                {activeTab === 'archives' ? <ArchiveIcon className="size-8 md:size-10 text-slate-400" /> : <BookmarkIcon className="size-8 md:size-10 text-slate-400" />}
              </div>
              <h3 className="text-2xl md:text-3xl font-extrabold font-outfit mb-3 md:mb-4">Aucun élément trouvé</h3>
              <p className="max-w-md mx-auto text-slate-500 dark:text-slate-400 text-base md:text-lg">
                {activeTab === 'saved'
                  ? "Votre dossier de favoris est vide. Explorez le Hub pour sauvegarder vos opportunités."
                  : activeTab === 'archives'
                  ? "Les concours clôturés et ceux dont la date est inconnue apparaissent ici automatiquement."
                  : "Le flux est actuellement vide. Lance le scraper Python pour rafraîchir les données."}
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Footer — extra bottom padding on mobile for the bottom nav bar */}
      <footer className="py-10 md:py-16 pb-24 md:pb-16 mt-12 border-t border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 backdrop-blur-lg">
        <div className="flex flex-col items-center justify-between gap-4 px-6 mx-auto max-w-7xl md:flex-row">
          <div className="flex items-center gap-4">
            <span className="text-xl md:text-2xl font-bold tracking-widest font-serif text-slate-900 dark:text-white">
              ARCHI<span className="text-[#a68a30] dark:text-[#c2a65a]">.</span>SPACE
            </span>
          </div>
          <p className="text-xs md:text-sm font-semibold text-slate-500 dark:text-slate-400 text-center uppercase tracking-widest">
            © {new Date().getFullYear()} Archi Space — Tous droits réservés
          </p>
        </div>
      </footer>

      <style dangerouslySetInnerHTML={{__html: `
        .hidescrollbar::-webkit-scrollbar { display: none; }
        .hidescrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        .safe-area-pb { padding-bottom: max(env(safe-area-inset-bottom, 0px), 4px); }
      `}} />
    </div>
  );
}
