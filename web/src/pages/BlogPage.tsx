import { Link } from 'react-router-dom';
import { api } from '../lib/api';

export interface BlogPost {
  slug: string;
  title: string;
  date: string;
  excerpt: string;
  content: string;
}

import intro from '../content/intro.md?raw';
import district_guide from '../content/district-guide.md?raw';
import quiet_hours from '../content/quiet-hours.md?raw';

function parse(raw: string, slug: string): BlogPost {
  const meta = raw.split('---')[1] ?? '';
  const body = (raw.split('---')[2] ?? raw).trim();
  const get = (k: string) => (meta.match(new RegExp(`^${k}:(.*)$`, 'm'))?.[1] ?? '').trim();
  return {
    slug,
    title: get('title') || slug,
    date: get('date') || '2026-01-01',
    excerpt: get('excerpt') || body.slice(0, 140),
    content: body,
  };
}

export const posts: BlogPost[] = [
  parse(intro, 'toshkentda-ishlash-uchun-joy'),
  parse(district_guide, 'tumanlar-bo-yicha-qo-llanma'),
  parse(quiet_hours, 'eng-tinch-soatlar'),
];

export default function BlogPage() {
  api.stats().catch(() => undefined); // warm api
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="font-heading text-3xl font-bold">Blog</h1>
      <p className="text-muted mt-2">Toshkentda masofadan ishlash bo'yicha qo'llanmalar</p>
      <div className="grid gap-4 mt-8">
        {posts.map((p) => (
          <Link key={p.slug} to={`/blog/${p.slug}`} className="card hover:border-cyan/50 transition-colors">
            <p className="text-muted text-xs">{p.date}</p>
            <h2 className="font-heading text-xl font-semibold mt-1">{p.title}</h2>
            <p className="text-muted text-sm mt-2">{p.excerpt}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
