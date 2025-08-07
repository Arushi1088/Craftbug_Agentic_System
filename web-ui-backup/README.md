# 🌐 UX Analyzer Web Interface

A modern React web application providing an intuitive interface for comprehensive UX analysis with scenario testing, visual reporting, and API integration.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Running UX Analyzer backend (FastAPI server on port 8000)

### Installation & Development
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open browser to http://localhost:3000
```

### Production Build
```bash
# Build for production
npm run build

# Preview production build  
npm run preview
```

## 📋 Features

### Analysis Capabilities
- **URL Analysis**: Live website comprehensive UX auditing
- **Screenshot Analysis**: Visual analysis of design mockups
- **URL + Scenario**: Website testing with YAML scenarios
- **Mock + Scenario**: Prototype testing with user journeys

### Reporting & Visualization
- **Interactive Charts**: Plotly.js visualizations for analysis data
- **Dual View Mode**: Visual reports and raw JSON data view
- **Download Options**: Export reports in JSON and HTML formats
- **Real-time Results**: Live analysis progress and results

### User Experience
- **Responsive Design**: Mobile-first responsive layout
- **Form Validation**: Real-time input validation and error handling
- **Loading States**: Progress indicators and status feedback
- **Accessibility**: Keyboard navigation and screen reader support

## 🗂️ Project Structure

```
src/
├── components/
│   └── Navigation.tsx          # Main navigation bar
├── pages/
│   ├── HomePage.tsx             # Landing page with feature overview
│   ├── AnalysisPage.tsx         # Analysis form and submission
│   └── EnhancedReportPage.tsx   # Advanced report viewer with charts
├── App.tsx                      # Main application with routing
├── main.tsx                     # Application entry point
└── index.css                    # Global styles with Tailwind
```

## 🔧 Configuration

### API Integration
The application connects to the FastAPI backend via proxy configuration:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      secure: false,
    }
  }
}
```

### Environment Variables
```bash
# .env.local (optional)
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE="UX Analyzer"
```

## 📊 Analysis Workflow

### 1. Select Analysis Mode
Choose from four analysis types:
- **URL Analysis**: Basic website audit
- **Screenshot Analysis**: Visual UX evaluation  
- **URL + Scenario**: Website with predefined test scenarios
- **Mock + Scenario**: Prototype with user journey testing

### 2. Configure Analysis
- **Target Input**: URL, file upload, or app path
- **Scenario Selection**: Choose from available YAML scenarios
- **Module Selection**: Enable/disable analysis modules
- **Output Format**: Select JSON or HTML report format

### 3. Review Results
- **Visual Reports**: Interactive charts and score breakdowns
- **JSON View**: Raw data with collapsible tree structure
- **Download**: Export reports for sharing and archival
- **Analysis Details**: Scenario steps and module findings

## 🎨 Design System

### Color Palette
- **Primary**: Blue (#3B82F6) for actions and navigation
- **Success**: Green (#10B981) for scores 80+
- **Warning**: Yellow (#F59E0B) for scores 60-79
- **Error**: Red (#EF4444) for scores <60
- **Neutral**: Gray scale for text and backgrounds

### Typography
- **Headings**: System font stack with bold weights
- **Body**: Regular weight with optimal line height
- **Code**: Monospace for technical content
- **UI Text**: Medium weight for labels and controls

### Components
- **Cards**: Rounded corners with subtle shadows
- **Buttons**: Consistent padding and hover states
- **Forms**: Clear labels with inline validation
- **Charts**: Responsive with consistent color coding

## 📱 Responsive Design

### Breakpoints
- **Mobile**: 320px - 768px (1 column layout)
- **Tablet**: 768px - 1024px (2 column layout)
- **Desktop**: 1024px+ (3 column layout)

### Mobile Features
- **Touch-friendly**: Larger touch targets for mobile
- **Optimized Forms**: Mobile-specific input types
- **Responsive Charts**: Auto-scaling visualizations
- **Hamburger Menu**: Collapsible navigation on small screens

## 🧪 Testing

### Manual Testing Checklist
- [ ] Form submission for all analysis modes
- [ ] Error handling for invalid inputs
- [ ] Chart rendering and interactivity
- [ ] Mobile responsiveness
- [ ] API integration and error states
- [ ] Report generation and downloads

### Automated Testing (Future)
```bash
# Unit tests with Jest
npm run test

# E2E tests with Playwright
npm run test:e2e

# Visual regression tests
npm run test:visual
```

## 🔗 API Integration

### Endpoints Used
- `GET /api/scenarios` - Load available YAML scenarios
- `POST /api/analyze` - Submit basic analysis
- `POST /api/analyze/url-scenario` - Submit URL + scenario analysis
- `POST /api/analyze/mock-scenario` - Submit mock + scenario analysis
- `GET /api/reports/{id}` - Fetch analysis results
- `GET /api/reports/{id}/download` - Download report files

### Error Handling
- **Network Errors**: Connection timeout and retry logic
- **Validation Errors**: Field-level error display
- **API Errors**: User-friendly error messages
- **Loading States**: Progress indicators during requests

## 🚀 Deployment

### Docker Deployment
```dockerfile
# Multi-stage build
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

### Nginx Configuration
```nginx
server {
  listen 80;
  location / {
    root /usr/share/nginx/html;
    try_files $uri $uri/ /index.html;
  }
  location /api {
    proxy_pass http://backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

### Environment-specific Builds
```bash
# Development
npm run dev

# Staging
npm run build:staging

# Production
npm run build
```

## 📈 Performance Optimization

### Build Optimization
- **Code Splitting**: Lazy loading for route components
- **Tree Shaking**: Remove unused code from bundles
- **Asset Optimization**: Image compression and minification
- **Bundle Analysis**: Webpack bundle analyzer for size optimization

### Runtime Performance
- **React.memo**: Prevent unnecessary re-renders
- **useMemo/useCallback**: Optimize expensive computations
- **Lazy Loading**: Load components and data on demand
- **Error Boundaries**: Graceful error handling

### Monitoring
- **Core Web Vitals**: LCP, FID, CLS tracking
- **User Analytics**: User interaction and conversion tracking
- **Error Tracking**: Runtime error monitoring and reporting
- **Performance Metrics**: API response times and render performance

## 🔒 Security Considerations

### Client-side Security
- **Input Validation**: Sanitize all user inputs
- **XSS Prevention**: Escape user-generated content
- **CSRF Protection**: Token-based request validation
- **Content Security Policy**: Restrict resource loading

### API Security
- **Authentication**: JWT token-based auth (future)
- **Authorization**: Role-based access control
- **Rate Limiting**: Prevent API abuse
- **HTTPS Only**: Secure communication in production

## 🛠️ Development

### Development Server
```bash
# Start with hot reload
npm run dev

# Start with network access
npm run dev -- --host

# Start with specific port
npm run dev -- --port 3001
```

### Code Quality
```bash
# Linting
npm run lint

# Type checking
npm run type-check

# Formatting
npm run format
```

### Debugging
- **React DevTools**: Component inspection and state debugging
- **Network Tab**: API request/response debugging
- **Console Logs**: Strategic logging for development
- **Source Maps**: Debugging production builds

## 📚 Dependencies

### Core Dependencies
- **react**: UI library for component-based architecture
- **react-router-dom**: Client-side routing and navigation
- **react-plotly.js**: Interactive chart and data visualization
- **react-json-view**: JSON data viewer with collapsible tree
- **lucide-react**: Modern icon library
- **axios**: HTTP client for API communication

### Development Dependencies
- **typescript**: Type safety and development tooling
- **vite**: Fast build tool and development server
- **tailwindcss**: Utility-first CSS framework
- **eslint**: Code linting and style enforcement
- **@types/***: TypeScript type definitions

## 🤝 Contributing

### Development Workflow
1. **Clone Repository**: Get the latest code
2. **Install Dependencies**: `npm install`
3. **Start Backend**: Run FastAPI server on port 8000
4. **Start Frontend**: `npm run dev`
5. **Make Changes**: Implement features or fixes
6. **Test Changes**: Manual and automated testing
7. **Submit PR**: Code review and merge

### Code Standards
- **TypeScript**: Full type safety required
- **ESLint**: Follow configured linting rules
- **Component Structure**: Functional components with hooks
- **File Naming**: PascalCase for components, camelCase for utilities

---

## 🎯 Next Steps

Ready for production deployment with comprehensive UX analysis capabilities! 🚀

For additional documentation, see:
- [API Documentation](../docs/API.md)
- [Deployment Guide](../docs/DEPLOYMENT.md)
- [Testing Guide](../docs/TESTING.md)
