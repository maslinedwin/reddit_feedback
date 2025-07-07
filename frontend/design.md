## Design System

### Color Palette
- **Primary**: `#514DFB` (purple) - Main brand color
- **Primary Hover**: `#427095`
- **Secondary**: `#DDF0FF` (light blue)
- **Success**: `#24c46e` (green)
- **Error**: `#fd4e30` (red)
- **Warning**: `#ffb723` (mango)
- **Dark**: `#1d1d22` - Dark backgrounds
- **Gray Scale**: `gray-50` to `gray-900`
- **Button Blue**: `#037aff` - CTAs
- **Overlay**: `rgba(30, 30, 32, 0.7)` - Modal overlays

### Typography
- **Font Family**: Proxima Nova Rg (primary), Muli, Avenir, Montserrat
- **Font Sizes**: Use Tailwind classes `text-xs` to `text-6xl`
- **Line Heights**: `leading-tight` to `leading-loose`
- **Letter Spacing**: Custom values from `-1.8px` to `3px`

### Component Patterns

#### Buttons
```tsx
// Primary Button
<button className="bg-primary hover:bg-primary-hover text-white px-6 py-3 rounded-lg">

// Secondary Button  
<button className="bg-secondary hover:bg-secondary-hover text-primary px-6 py-3 rounded-lg">

// Ghost Button
<button className="border border-gray-300 hover:bg-gray-50 px-6 py-3 rounded-lg">
```

#### Cards
```tsx
// Base Card
<div className="bg-white rounded-2xl shadow-lg p-6">

// Glassmorphism Card
<div className="bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 p-6">

// Dashboard Card (with gradient)
<div className="bg-gradient-to-r from-primary to-primary-light rounded-2xl p-6">
```

#### Modals
```tsx
// Desktop Modal
<div className="fixed inset-0 bg-overlay z-50 flex items-center justify-center">
  <div className="bg-white rounded-2xl max-w-lg w-full p-6">
    <h2 className="text-2xl font-bold mb-4">Modal Title</h2>
    {/* Content */}
  </div>
</div>

// Mobile Bottom Sheet
<Sheet isOpen={open} onClose={onClose}>
  <Sheet.Container>
    <Sheet.Header />
    <Sheet.Content>
      {/* Content */}
    </Sheet.Content>
  </Sheet.Container>
</Sheet>
```

### Spacing & Layout
- **Container**: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`
- **Section Padding**: `py-12 sm:py-16 lg:py-20`
- **Card Spacing**: `space-y-4` or `gap-4` in grid
- **Form Spacing**: `space-y-6` between form groups

### Responsive Design
- **Mobile First**: Start with mobile styles, add desktop with `sm:`, `md:`, `lg:`, `xl:`
- **Breakpoints**: `xs: 320px`, `sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`
- **Grid System**: Use Tailwind's grid with responsive columns

### Animation & Transitions
- **Default Transition**: `transition-all duration-300 ease-in-out`
- **Hover Effects**: Scale, shadow, color transitions
- **Loading States**: Use skeleton loaders or spinners
- **Page Transitions**: Fade in/out with opacity

### Form Elements
```tsx
// Input Field
<input className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-primary focus:ring-2 focus:ring-primary/20">

// Select Dropdown
<select className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:border-primary">

// Checkbox/Radio
<input type="checkbox" className="w-4 h-4 text-primary rounded focus:ring-primary">
```

### Icons & Assets
- **Icon Library**: React Icons, Heroicons, Lucide React
- **Image Optimization**: Use Next.js Image component
- **SVG Usage**: Inline for icons, optimize with SVGO

