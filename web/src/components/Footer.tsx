export default function Footer() {
  return (
    <footer className="border-t border-border bg-bg2/50">
      <div className="max-w-6xl mx-auto px-4 py-8 grid gap-6 sm:grid-cols-3 text-sm">
        <div>
          <p className="font-heading font-bold">
            <span className="text-cyan">Quiet</span>
            <span className="text-violet">Space</span>
          </p>
          <p className="text-muted mt-2">
            Toshkentdagi tinch ishlash joylarini topish platformasi
          </p>
        </div>
        <div className="text-muted">
          <p className="text-text font-medium mb-2">Bo'limlar</p>
          <p>Xarita</p>
          <p>AI yordamchi</p>
          <p>Telegram bot</p>
        </div>
        <div className="text-muted">
          <p className="text-text font-medium mb-2">Aloqa</p>
          <p>hello@quietspace.uz</p>
          <p>Tashkent, Uzbekistan</p>
        </div>
      </div>
      <div className="border-t border-border text-center text-xs text-muted py-4">
        © 2026 QuietSpace Tashkent
      </div>
    </footer>
  );
}
