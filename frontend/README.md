# DataLens AI - Frontend

Modern React application for AI-powered data intelligence and visualization.

## 🛠️ Tech Stack

- **React 19** - Latest React with modern hooks and features
- **Vite 7** - Lightning-fast build tool with HMR
- **Tailwind CSS v4** - Utility-first CSS framework
- **Chart.js 4** - Professional chart visualizations
- **React-ChartJS-2** - React wrapper for Chart.js
- **Three.js** - 3D graphics for interactive backgrounds

## 📁 Project Structure

```
src/
├── components/
│   ├── Navbar.jsx           # Top navigation bar
│   ├── Sidebar.jsx          # Left sidebar with history
│   ├── QueryBox.jsx         # Query input and suggestions
│   ├── ChartsGrid.jsx       # Chart display grid
│   ├── StatsGrid.jsx        # Statistics cards
│   ├── Overview.jsx         # Data overview component
│   ├── Summary.jsx          # Data summary panel
│   ├── Loading.jsx          # Loading states
│   ├── ErrorBanner.jsx      # Error displays
│   ├── EmptyState.jsx       # Empty state UI
│   ├── Header.jsx           # Section headers
│   ├── HistoryPanel.jsx     # Query history
│   └── ThreeBackground.jsx  # 3D animated background
├── assets/                   # Static assets
├── App.jsx                   # Main application component
├── main.jsx                  # React entry point
└── index.css                 # Global styles and Tailwind

public/                       # Public static files
```

## 🚀 Development

### Install Dependencies
```bash
npm install
```

### Start Development Server
```bash
npm run dev
```

Runs on `http://localhost:5173` with hot module replacement (HMR).

### Build for Production
```bash
npm run build
```

Creates optimized production build in `dist/` directory.

### Preview Production Build
```bash
npm run preview
```

### Lint Code
```bash
npm run lint
```

## 🎨 Key Components

### App.jsx
Main application component that:
- Manages global state (uploaded data, queries, history)
- Handles API communication with Flask backend
- Coordinates component interactions
- Manages loading and error states

### ChartsGrid.jsx
Renders chart visualizations using Chart.js:
- Supports multiple chart types (bar, line, pie, scatter, etc.)
- Responsive grid layout
- Interactive tooltips and legends
- Dynamic color schemes

### QueryBox.jsx
Natural language query interface:
- Text input with suggestions
- AI-powered query recommendations
- Real-time validation
- Query history integration

### ThreeBackground.jsx
Animated 3D background:
- Interactive particle effects
- Responsive to mouse movement
- Optimized performance
- Optional enable/disable

## 🔧 Configuration

### Vite Configuration
See `vite.config.js` for:
- React plugin setup
- Build optimization
- Asset handling
- Dev server configuration

### ESLint Configuration
See `eslint.config.js` for:
- React rules
- React Hooks rules
- Code quality standards

### Tailwind Configuration
Tailwind v4 is configured via CSS in `src/index.css`:
- Custom theme colors
- Custom utilities
- Responsive breakpoints
- Dark mode support

## 🌐 API Integration

### Backend Endpoints

The frontend connects to Flask backend at `http://localhost:5000`:

```javascript
// Upload CSV
POST /upload
FormData: { file: File }

// Query data
POST /query
Body: { query: string, csv_data: object }

// Generate dashboard
POST /generate-dashboard
Body: { query: string, csv_data: object }
```

### Environment Variables

Create `.env` in frontend directory if needed:
```env
VITE_API_URL=http://localhost:5000
```

## 📱 Responsive Design

- **Desktop**: Full layout with sidebar and grid
- **Tablet**: Collapsible sidebar, responsive grid
- **Mobile**: Stacked layout, optimized for touch

## 🎨 Styling Guide

### Tailwind Classes
The project uses Tailwind CSS v4 utility classes:
- Layout: `flex`, `grid`, `container`
- Spacing: `p-4`, `m-2`, `gap-4`
- Colors: `bg-gray-900`, `text-white`
- Effects: `shadow-lg`, `hover:scale-105`

### Custom Styles
Global styles in `index.css`:
- CSS variables for theming
- Custom animations
- Font imports
- Base resets

## 🚀 Performance Optimization

### Implemented
- Code splitting with React lazy loading
- Memoization with React.memo and useMemo
- Debounced API calls
- Optimized chart rendering
- Efficient state management

### Best Practices
- Keep components small and focused
- Use React DevTools to profile
- Minimize re-renders with proper dependencies
- Lazy load heavy components (Three.js)

## 🧪 Testing

### Manual Testing
- Test file upload functionality
- Verify chart rendering
- Check responsive layouts
- Test error handling

### Browser Compatibility
- Chrome/Edge: ✅ Fully supported
- Firefox: ✅ Fully supported
- Safari: ✅ Fully supported
- Mobile browsers: ✅ Responsive

## 🐛 Common Issues

### HMR Not Working
- Clear browser cache
- Restart dev server
- Check for syntax errors

### Charts Not Displaying
- Check browser console for errors
- Verify Chart.js is loaded
- Check data format from API

### Build Fails
- Delete `node_modules` and reinstall
- Clear vite cache: `rm -rf node_modules/.vite`
- Check for dependency conflicts

## 📚 Resources

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vite.dev)
- [Tailwind CSS v4](https://tailwindcss.com/docs)
- [Chart.js Documentation](https://www.chartjs.org/docs)
- [Three.js Documentation](https://threejs.org/docs)

## 🤝 Contributing

When contributing to the frontend:
1. Follow the existing component structure
2. Use functional components with hooks
3. Maintain consistent styling with Tailwind
4. Add PropTypes for component props
5. Test across different browsers

---

**Part of DataLens AI - GenAI Data Intelligence Dashboard**
