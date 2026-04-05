'use client';

import { useState, useEffect, useCallback } from 'react';
import { Header } from "@/components/ui/header-1";
import { Button } from "@/components/ui/button";
import { BookmarkIcon, ExternalLinkIcon, RefreshCwIcon, MapPinIcon, CalendarIcon, BriefcaseIcon, NewspaperIcon, TrophyIcon, MoonIcon, SunIcon, ArchiveIcon, ArrowRightIcon } from "lucide-react";
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
  date?: string;
}

type TabType = 'competitions' | 'jobs' | 'news' | 'saved' | 'archives';

export default function Home() {
  const [competitions, setCompetitions] = useState<ContentItem[]>([]);
  const [jobs, setJobs] = useState<ContentItem[]>([]);
  const [news, setNews] = useState<ContentItem[]>([]);
  const [savedItems, setSavedItems] = useState<ContentItem[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('competitions');
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
      const [compRes, jobsRes, newsRes] = await Promise.all([
        fetch('/competitions.json'),
        fetch('/jobs.json'),
        fetch('/news.json')
      ]);

      if (compRes.ok) setCompetitions(await compRes.json());
      if (jobsRes.ok) setJobs(await jobsRes.json());
      if (newsRes.ok) setNews(await newsRes.json());
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

  const getDisplayedItems = () => {
    const today = new Date();
    
    // Sort logic (newest deadlines first)
    const sortByDeadline = (a: ContentItem, b: ContentItem) => {
      if (a.deadline_iso && b.deadline_iso) return new Date(a.deadline_iso).getTime() - new Date(b.deadline_iso).getTime();
      return 0;
    };

    if (activeTab === 'competitions') {
      return competitions.filter(item => {
        if (!item.deadline_iso) return false; // Hide items with unknown deadlines
        const d = parseISO(item.deadline_iso);
        return isValid(d) && differenceInDays(d, today) >= 0;
      }).sort(sortByDeadline);
    }
    if (activeTab === 'archives') {
      return competitions.filter(item => {
        if (!item.deadline_iso) return true; // Show items with unknown deadlines
        const d = parseISO(item.deadline_iso);
        return isValid(d) && differenceInDays(d, today) < 0;
      }).sort((a,b) => -sortByDeadline(a,b)); // latest expired first
    }
    if (activeTab === 'jobs') return jobs;
    if (activeTab === 'news') return news;
    return savedItems;
  };

  const displayedItems = getDisplayedItems();

  return (
    <div className="relative flex min-h-screen flex-col font-inter bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-50 transition-colors selection:bg-indigo-500/20">
      
      {/* Premium Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
        {/* Light Mode Blobs */}
        <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] rounded-full bg-indigo-500/10 dark:bg-indigo-500/5 blur-[120px]" />
        <div className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] rounded-full bg-amber-500/5 dark:bg-rose-500/5 blur-[120px]" />
        
        {/* Architect Geometry Overlay (subtle grid) */}
        <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))] dark:opacity-20 opacity-30" />
      </div>

      <Header />

      <main className="flex-grow z-10 w-full mb-16 px-6 lg:px-8">
        
        {/* PREMIUM TYPOGRAPHIC HERO CONCEPT */}
        <section className="relative w-full mx-auto max-w-7xl pt-20 pb-20 overflow-hidden rounded-3xl border border-slate-200 dark:border-slate-800 shadow-sm dark:shadow-none bg-white dark:bg-[#0a0a0d] mb-12 mt-4 px-8 lg:px-16 flex flex-col justify-center">
          
          {/* Controls Container */}
          <div className="absolute top-6 right-6 flex items-center gap-4 z-50">
              <Button
                variant="outline"
                size="sm"
                onClick={fetchData}
                disabled={loading}
                className="rounded-none border-slate-300 dark:border-slate-800 bg-transparent text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-900 uppercase tracking-widest text-xs h-10 px-4"
              >
                <RefreshCwIcon className={cn("mr-2 size-3", loading && "animate-spin")} /> Sync
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

          <div className="relative z-10 max-w-4xl pt-12 pb-24">
            <div className="flex items-center gap-4 mb-10">
              <div className="h-px w-12 bg-[#a68a30] dark:bg-[#c2a65a]"></div>
              <span className="text-[#a68a30] dark:text-[#c2a65a] uppercase font-bold tracking-[0.2em] text-sm">FUTUR ARCHITECTE</span>
            </div>
            
            <h1 className="text-6xl md:text-8xl lg:text-[110px] leading-[1] text-slate-900 dark:text-white font-serif mb-10 select-none tracking-tight">
              <span className="block">Construis</span>
              <span className="block"><span className="italic text-[#a68a30] dark:text-[#c2a65a] pr-4 font-light">ton</span>avenir</span>
              <span className="block text-transparent [-webkit-text-stroke:1px_rgba(15,23,42,0.4)] dark:[-webkit-text-stroke:1px_rgba(255,255,255,0.4)]">maintenant.</span>
            </h1>
            
            <p className="max-w-xl text-lg md:text-xl text-slate-600 dark:text-slate-400 font-light mb-12">
              Concours, jobs, news — tout ce dont tu as besoin pour <strong className="text-slate-900 dark:text-white font-medium">lancer ta carrière</strong>, agrégé et mis à jour en temps réel.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 max-w-2xl">
              <Button 
                size="lg" 
                className="rounded-none font-semibold px-8 py-7 bg-[#a68a30] dark:bg-[#c2a65a] text-white dark:text-slate-950 hover:bg-[#8a7224] dark:hover:bg-[#d8be72] transition-colors uppercase tracking-wider text-sm w-full sm:w-auto" 
                onClick={() => { document.getElementById('hub-content')?.scrollIntoView({ behavior: 'smooth' }); setActiveTab('competitions'); }}
              >
                EXPLORER LES CONCOURS <ArrowRightIcon className="ml-4 w-4 h-4"/>
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="rounded-none px-8 py-7 bg-transparent border border-slate-300 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors uppercase tracking-wider text-sm w-full sm:w-auto" 
                onClick={() => { document.getElementById('hub-content')?.scrollIntoView({ behavior: 'smooth' }); setActiveTab('jobs'); }}
              >
                VOIR LES OFFRES D&apos;EMPLOI <ArrowRightIcon className="ml-4 w-4 h-4"/>
              </Button>
            </div>
          </div>

          {/* MASSIVE BACKGROUND TEXT */}
          <div className="absolute bottom-[-15%] xl:bottom-[-20%] left-0 right-0 overflow-hidden pointer-events-none select-none z-0 opacity-5 dark:opacity-10">
            <h2 className="text-[30vw] font-serif leading-none whitespace-nowrap text-slate-900 dark:text-white text-center tracking-tighter">ARCH</h2>
          </div>
        </section>

        {/* Tab Navigation System */}
        <div id="hub-content" className="max-w-7xl px-6 py-12 mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 mb-10">
            
            {/* Minimalist Tabs */}
            <div className="flex space-x-2 border-b border-slate-200 dark:border-slate-800 overflow-x-auto w-full md:w-auto hidescrollbar">
              <button
                onClick={() => setActiveTab('competitions')}
                className={cn(
                  "flex items-center gap-2 px-4 py-4 text-sm font-semibold tracking-wide transition-all duration-300 border-b-2 whitespace-nowrap",
                  activeTab === 'competitions' ? "border-[#a68a30] dark:border-[#c2a65a] text-slate-900 dark:text-white" : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
                )}
              >
                <TrophyIcon className="w-4 h-4" /> Concours
              </button>
              
              <button
                onClick={() => setActiveTab('jobs')}
                className={cn(
                  "flex items-center gap-2 px-4 py-4 text-sm font-semibold tracking-wide transition-all duration-300 border-b-2 whitespace-nowrap",
                  activeTab === 'jobs' ? "border-[#a68a30] dark:border-[#c2a65a] text-slate-900 dark:text-white" : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
                )}
              >
                <BriefcaseIcon className="w-4 h-4" /> Jobs
              </button>

              <button
                onClick={() => setActiveTab('news')}
                className={cn(
                  "flex items-center gap-2 px-4 py-4 text-sm font-semibold tracking-wide transition-all duration-300 border-b-2 whitespace-nowrap",
                  activeTab === 'news' ? "border-[#a68a30] dark:border-[#c2a65a] text-slate-900 dark:text-white" : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
                )}
              >
                <NewspaperIcon className="w-4 h-4" /> Actualités
              </button>

              <button
                onClick={() => setActiveTab('saved')}
                className={cn(
                  "flex items-center gap-2 px-4 py-4 text-sm font-semibold tracking-wide transition-all duration-300 border-b-2 whitespace-nowrap",
                  activeTab === 'saved' ? "border-[#a68a30] dark:border-[#c2a65a] text-slate-900 dark:text-white" : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
                )}
              >
                <BookmarkIcon className="w-4 h-4" /> Favoris
                {savedItems.length > 0 && (
                  <span className={cn("flex items-center justify-center px-2 py-0.5 ml-1 text-xs text-white rounded-full", activeTab === 'saved' ? "bg-[#a68a30] dark:bg-[#c2a65a]" : "bg-slate-300 dark:bg-slate-700")}>
                    {savedItems.length}
                  </span>
                )}
              </button>
              
              <button
                onClick={() => setActiveTab('archives')}
                className={cn(
                  "flex items-center gap-2 px-4 py-4 text-sm font-semibold tracking-wide transition-all duration-300 border-b-2 whitespace-nowrap",
                  activeTab === 'archives' ? "border-[#a68a30] dark:border-[#c2a65a] text-slate-900 dark:text-white" : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
                )}
              >
                <ArchiveIcon className="w-4 h-4" /> Archives
              </button>
            </div>
          </div>

          {/* Cards Grid */}
          {loading ? (
             <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
               {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
                 <div key={i} className="h-[320px] rounded-[2rem] bg-slate-200/50 dark:bg-slate-800/50 animate-pulse border border-slate-200 dark:border-slate-800 shadow-sm" />
               ))}
             </div>
          ) : displayedItems.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
              {displayedItems.map((item, i) => {
                const isItemSaved = isSaved(item.link);
                const TypeIcon = item.type === 'competition' ? TrophyIcon : item.type === 'job' ? BriefcaseIcon : NewspaperIcon;
                
                // Highlight ending soon for competitions
                const isEndingSoon = item.type === 'competition' && activeTab === 'competitions' && item.deadline_iso && differenceInDays(parseISO(item.deadline_iso), new Date()) <= 14;

                return (
                 <div
                  key={`${item.link}-${i}`}
                  className={cn(
                    "group relative flex flex-col h-full gap-5 p-7 transition-all duration-500 border shadow-md bg-white dark:bg-slate-900 rounded-[2rem] hover:shadow-xl hover:-translate-y-2",
                    "border-slate-200 dark:border-slate-800",
                    isEndingSoon && "ring-2 ring-rose-500/50 border-rose-500/50"
                  )}
                 >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex flex-col gap-2 flex-grow">
                      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold tracking-wider uppercase rounded-full w-fit bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                         <TypeIcon className="w-3.5 h-3.5" />
                         {item.type || 'Article'}
                      </span>
                      
                      {/* Meta information tags */}
                      {item.type === 'competition' && item.deadline && (
                         <span className={cn(
                           "flex items-center gap-1.5 text-xs font-bold",
                           activeTab === 'archives' ? "text-slate-500" : isEndingSoon ? "text-rose-500" : "text-emerald-600 dark:text-emerald-400"
                         )}>
                           <CalendarIcon className="w-3.5 h-3.5" /> 
                           {activeTab === 'archives' ? `Clôturé le ${item.deadline}` : item.deadline}
                         </span>
                      )}
                      {item.type === 'job' && item.location && (
                         <span className="flex items-center gap-1.5 text-xs font-bold text-indigo-600 dark:text-indigo-400">
                           <MapPinIcon className="w-3.5 h-3.5" /> {item.location}
                         </span>
                      )}
                    </div>

                    <button
                      onClick={() => toggleSave(item)}
                      className={cn(
                        "rounded-full p-3 transition-colors shadow-sm border",
                        isItemSaved 
                          ? "text-[#a68a30] bg-[#a68a30]/10 border-[#a68a30]/20 dark:text-[#c2a65a] dark:bg-[#c2a65a]/10 dark:border-[#c2a65a]/20" 
                          : "text-slate-400 bg-white dark:bg-slate-800 border-slate-100 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700",
                      )}
                    >
                      <BookmarkIcon className={cn("size-4.5", isItemSaved && "fill-current")} />
                    </button>
                  </div>

                  <h3 className="text-xl font-extrabold font-outfit leading-tight text-slate-800 dark:text-slate-100 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors line-clamp-3">
                    {item.title}
                  </h3>

                  <p className="text-sm font-medium leading-relaxed text-slate-500 dark:text-slate-400 line-clamp-3 flex-grow pb-4">
                    {item.description || "Aucun résumé disponible pour cet élément."}
                  </p>

                  <div className="pt-5 mt-auto border-t border-slate-100 dark:border-slate-800">
                    <a
                      href={item.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex w-full items-center justify-center gap-2 py-2.5 px-4 text-sm font-bold tracking-wide text-slate-900 bg-slate-100 hover:bg-slate-200 dark:text-white dark:bg-slate-800 dark:hover:bg-slate-700 rounded-none transition-all uppercase"
                    >
                      Consulter {activeTab === 'archives' ? "l'archive" : "l'offre"} <ExternalLinkIcon className="size-4" />
                    </a>
                  </div>
                </div>
                );
              })}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center p-16 text-center rounded-[3rem] bg-white/40 dark:bg-slate-900/40 backdrop-blur-md border border-slate-200 dark:border-slate-800 shadow-inner min-h-[400px]">
              <div className="p-6 mb-8 rounded-full bg-slate-100 dark:bg-slate-800 shadow-sm">
                {activeTab === 'archives' ? <ArchiveIcon className="size-10 text-slate-400" /> : <BookmarkIcon className="size-10 text-slate-400" />}
              </div>
              <h3 className="text-3xl font-extrabold font-outfit mb-4">Aucun élément trouvé</h3>
              <p className="max-w-md mx-auto text-slate-500 dark:text-slate-400 text-lg">
                {activeTab === 'saved'
                  ? "Votre dossier de favoris est vide. Explorez le Hub pour sauvegarder vos opportunités."
                  : activeTab === 'archives'
                  ? "Aucun concours expiré n'est présent dans la base de données."
                  : "Le flux est actuellement vide. Lancez le scraper système (bouton Rapide Sync) pour le rafraîchir."}
              </p>
            </div>
          )}
        </div>
      </main>

      <footer className="py-16 mt-12 border-t border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 backdrop-blur-lg">
        <div className="flex flex-col items-center justify-between gap-6 px-6 mx-auto max-w-7xl md:flex-row">
          <div className="flex items-center gap-4">
            <span className="text-2xl font-bold tracking-widest font-serif text-slate-900 dark:text-white">
              ARCHI<span className="text-[#a68a30] dark:text-[#c2a65a]">.</span>SPACE
            </span>
          </div>
          <p className="text-sm font-semibold text-slate-500 dark:text-slate-400 text-center uppercase tracking-widest">
            © {new Date().getFullYear()} Minimalist Architect Suite
          </p>
        </div>
      </footer>
      
      {/* Hide scrollbar injected style & background pattern */}
      <style dangerouslySetInnerHTML={{__html: `
        .hidescrollbar::-webkit-scrollbar { display: none; }
        .hidescrollbar { -ms-overflow-style: none; scrollbar-width: none; }
        @keyframes slide { from { transform: translate(0, 0); } to { transform: translate(-40px, -40px); } }
      `}} />
    </div>
  );
}
