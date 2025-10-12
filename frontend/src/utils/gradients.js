// Modern Luxury gradient utilities for AdCopySurge
// Color Palette: #7C3AED (Primary), #A855F7 (Accent), #0F0B1D (Background), #F9FAFB (Text), #E5E7EB (Neutral), #C084FC (CTA)

export const gradients = {
  // === PRIMARY BRAND GRADIENTS - Modern Luxury ===
  primary: 'linear-gradient(135deg, #7C3AED 0%, #A855F7 50%, #C084FC 100%)',
  primaryLight: 'linear-gradient(135deg, #A855F7 0%, #C084FC 50%, #E9D5FF 100%)',
  primaryDark: 'linear-gradient(135deg, #5B21B6 0%, #7C3AED 50%, #A855F7 100%)',
  
  // === HERO & BACKGROUND GRADIENTS - Deep Navy/Black Base ===
  darkHero: 'linear-gradient(135deg, #0F0B1D 0%, #1A0F2E 50%, #2D1B4E 100%)',
  darkHeroRadial: 'radial-gradient(ellipse at top, #2D1B4E 0%, #1A0F2E 30%, #0F0B1D 100%)',
  darkSection: 'linear-gradient(180deg, #0F0B1D 0%, #1A0F2E 100%)',
  darkSectionAlt: 'linear-gradient(180deg, #1A0F2E 0%, #0F0B1D 100%)',
  
  // === CTA BUTTON GRADIENTS - Bright Gradient Purple ===
  ctaPrimary: 'linear-gradient(135deg, #C084FC 0%, #A855F7 50%, #7C3AED 100%)',
  ctaHover: 'linear-gradient(135deg, #E9D5FF 0%, #C084FC 50%, #A855F7 100%)',
  ctaActive: 'linear-gradient(135deg, #A855F7 0%, #7C3AED 100%)',
  
  // === ACCENT & HIGHLIGHT GRADIENTS ===
  accentGlow: 'linear-gradient(135deg, #A855F7 0%, #C084FC 100%)',
  accentSubtle: 'linear-gradient(135deg, rgba(168, 85, 247, 0.2) 0%, rgba(192, 132, 252, 0.1) 100%)',
  
  // === GLASS MORPHISM - Modern Luxury Edition ===
  glass: 'linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(192, 132, 252, 0.05) 100%)',
  glassDark: 'linear-gradient(135deg, rgba(15, 11, 29, 0.8) 0%, rgba(26, 15, 46, 0.9) 100%)',
  glassCard: 'linear-gradient(135deg, rgba(168, 85, 247, 0.08) 0%, rgba(45, 27, 78, 0.12) 100%)',
  glassCardHover: 'linear-gradient(135deg, rgba(168, 85, 247, 0.15) 0%, rgba(45, 27, 78, 0.2) 100%)',
  
  // === CARD BACKGROUNDS - Light & Dark Variants ===
  cardLight: 'linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%)',
  cardDark: 'linear-gradient(135deg, #1A0F2E 0%, #0F0B1D 100%)',
  cardPurple: 'linear-gradient(135deg, #2D1B4E 0%, #1A0F2E 100%)',
  cardGlow: 'linear-gradient(135deg, rgba(192, 132, 252, 0.15) 0%, rgba(168, 85, 247, 0.1) 100%)',
  
  // === PRICING CARDS ===
  pricingCard: 'linear-gradient(135deg, #1A0F2E 0%, #0F0B1D 100%)',
  pricingCardPopular: 'linear-gradient(135deg, #7C3AED 0%, #A855F7 50%, #C084FC 100%)',
  pricingCardHover: 'linear-gradient(135deg, #2D1B4E 0%, #1A0F2E 100%)',
  
  // === OVERLAYS & EFFECTS ===
  overlay: 'linear-gradient(180deg, rgba(15, 11, 29, 0) 0%, rgba(15, 11, 29, 0.8) 100%)',
  overlayRadial: 'radial-gradient(circle at center, rgba(168, 85, 247, 0.15) 0%, transparent 70%)',
  shimmer: 'linear-gradient(90deg, transparent 0%, rgba(192, 132, 252, 0.3) 50%, transparent 100%)',
  
  // === LEGACY COMPATIBILITY (for existing components) ===
  purple: 'linear-gradient(135deg, #7C3AED 0%, #A855F7 50%, #C084FC 100%)',
  purplePrimary: 'linear-gradient(135deg, #7C3AED 0%, #A855F7 50%, #C084FC 100%)',
  authBackground: 'linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%)',
  landingHero: 'linear-gradient(135deg, #0F0B1D 0%, #1A0F2E 50%, #2D1B4E 100%)',
  landingSection: 'linear-gradient(180deg, #0F0B1D 0%, #1A0F2E 100%)',
  landingAlternate: 'linear-gradient(180deg, #1A0F2E 0%, #0F0B1D 100%)',
  glassCardPurple: 'linear-gradient(135deg, rgba(168, 85, 247, 0.08) 0%, rgba(45, 27, 78, 0.12) 100%)',
};

// Helper function to create gradient backgrounds with fallbacks
export const createGradientBackground = (gradientName, fallbackColor = '#f8fafc') => ({
  background: gradients[gradientName] || gradients.softGray,
  backgroundAttachment: 'fixed',
  backgroundSize: 'cover',
  backgroundRepeat: 'no-repeat',
  minHeight: '100vh',
  // Fallback for older browsers
  backgroundColor: fallbackColor,
});

// Helper for creating gradient text
export const createGradientText = (gradientName) => ({
  background: gradients[gradientName] || gradients.primary,
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  backgroundClip: 'text',
  display: 'inline-block',
});

// Helper for creating gradient borders
export const createGradientBorder = (gradientName, borderWidth = '2px') => ({
  border: `${borderWidth} solid transparent`,
  backgroundImage: `${gradients[gradientName] || gradients.primary}, linear-gradient(white, white)`,
  backgroundClip: 'border-box, padding-box',
  backgroundOrigin: 'border-box, padding-box',
});

// Animation keyframes for gradient shifts
export const gradientAnimation = {
  backgroundSize: '200% 200%',
  animation: 'gradientShift 6s ease infinite',
  '@keyframes gradientShift': {
    '0%': {
      backgroundPosition: '0% 50%',
    },
    '50%': {
      backgroundPosition: '100% 50%',
    },
    '100%': {
      backgroundPosition: '0% 50%',
    },
  },
};

export default gradients;
