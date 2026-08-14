import { Navigate, Route, Routes } from 'react-router-dom';
import { isAuthed } from './lib/api';
import AppMapPage from './pages/AppMapPage';
import BlogPage from './pages/BlogPage';
import BlogPostPage from './pages/BlogPostPage';
import BusinessPage from './pages/BusinessPage';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import PlaceDetailPage from './pages/PlaceDetailPage';
import ProfilePage from './pages/ProfilePage';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

export default function App() {
  return (
    <div className="min-h-screen bg-bg text-text font-body flex flex-col">
      <Navbar />
      <div className="flex-1">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/business" element={<BusinessPage />} />
          <Route path="/blog" element={<BlogPage />} />
          <Route path="/blog/:slug" element={<BlogPostPage />} />
          <Route path="/app" element={<AppMapPage />} />
          <Route path="/app/places/:id" element={<PlaceDetailPage />} />
          <Route
            path="/app/profile"
            element={isAuthed() ? <ProfilePage /> : <Navigate to="/login" replace />}
          />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<LoginPage mode="register" />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
      <Footer />
    </div>
  );
}
