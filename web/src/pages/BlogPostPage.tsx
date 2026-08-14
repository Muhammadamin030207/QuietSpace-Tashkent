import { Link, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { posts } from './BlogPage';

export default function BlogPostPage() {
  const { slug } = useParams();
  const post = posts.find((p) => p.slug === slug);

  if (!post) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <p className="text-muted">Maqola topilmadi.</p>
        <Link to="/blog" className="text-cyan">← Blogga qaytish</Link>
      </div>
    );
  }

  return (
    <article className="max-w-3xl mx-auto px-4 py-12">
      <Link to="/blog" className="text-cyan text-sm">← Blog</Link>
      <p className="text-muted text-xs mt-4">{post.date}</p>
      <h1 className="font-heading text-3xl font-bold mt-1">{post.title}</h1>
      <div className="prose-custom mt-6 space-y-4 text-[15px] leading-relaxed">
        <ReactMarkdown
          components={{
            h2: ({ children }) => <h2 className="font-heading text-xl font-bold mt-6">{children}</h2>,
            p: ({ children }) => <p className="text-text/90">{children}</p>,
            a: ({ children, href }) => <a href={href} className="text-cyan">{children}</a>,
          }}
        >
          {post.content}
        </ReactMarkdown>
      </div>
    </article>
  );
}
