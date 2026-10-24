'use client';

import { useEffect, useState, useMemo } from 'react';
import { fetchCourses, Course } from '@/lib/courses';
import CourseCard from '@/components/CourseCard';

export default function HomePage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchCourses(200);
        if (!cancelled) setCourses(data);
      } catch (err) {
        console.error(err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    // Refresh periodically so new scraped courses appear
    const timer = setInterval(load, 60_000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return courses;
    return courses.filter((c) => c.course_title.toLowerCase().includes(q));
  }, [courses, search]);

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 shrink-0">
            <span className="text-2xl">🎓</span>
            <div>
              <h1 className="text-lg font-bold leading-none">
                <span className="brand-gradient-text">SHYAMAI</span>{' '}
                <span className="text-white">Learning Hub</span>
              </h1>
              <p className="text-xs mt-0.5 font-semibold tracking-wide">
                <span className="text-sky-400">Learn.</span>{' '}
                <span className="text-violet-400">Build.</span>{' '}
                <span className="text-pink-400">Grow.</span>
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-400 shrink-0">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse inline-block"></span>
            {loading ? '...' : `${courses.length} courses`}
          </div>
        </div>
      </header>

      {/* Hero + Search */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 pt-14 pb-10 text-center">
        <h2 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight mb-4">
          <span className="brand-gradient-text">SHYAMAI</span>{' '}
          <span className="text-white">Learning Hub</span>
        </h2>
        <p className="text-lg sm:text-xl md:text-2xl font-bold tracking-wide mb-10">
          <span className="text-sky-400">Learn.</span>{' '}
          <span className="text-violet-400">Build.</span>{' '}
          <span className="text-pink-400">Grow.</span>
        </p>

        {/* Search bar */}
        <div className="relative max-w-xl mx-auto">
          <svg
            className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500"
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M21 21l-4.35-4.35M17 11A6 6 0 115 11a6 6 0 0112 0z" />
          </svg>
          <input
            type="text"
            placeholder="Search courses..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 focus:border-sky-500 focus:ring-1 focus:ring-sky-500 rounded-xl pl-11 pr-4 py-3 text-sm text-white placeholder-gray-500 outline-none transition-colors"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
            >
              ✕
            </button>
          )}
        </div>

        {/* Search result count */}
        {search && !loading && (
          <p className="text-sm text-gray-500 mt-3">
            {filtered.length === 0
              ? 'No courses found'
              : `${filtered.length} course${filtered.length !== 1 ? 's' : ''} found`}
          </p>
        )}
      </section>

      {/* Grid */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 pb-16">
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="bg-gray-900 rounded-2xl border border-gray-800 animate-pulse">
                <div className="aspect-video bg-gray-800 rounded-t-2xl" />
                <div className="p-5 space-y-3">
                  <div className="h-3 bg-gray-800 rounded w-3/4" />
                  <div className="h-3 bg-gray-800 rounded w-1/2" />
                  <div className="h-8 bg-gray-800 rounded w-1/3 ml-auto" />
                </div>
              </div>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-24 text-gray-500">
            <div className="text-5xl mb-4">{search ? '🔍' : '📭'}</div>
            <p className="text-lg">{search ? `No courses match "${search}"` : 'No courses yet. Check back soon!'}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {filtered.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8 text-center text-xs text-gray-600">
        <p>Auto-updated every 5 min · Built by SHYAMAI</p>
      </footer>
    </div>
  );
}
