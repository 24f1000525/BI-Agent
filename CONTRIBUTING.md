# Contributing to DataLens AI

Thank you for your interest in contributing to DataLens AI! This guide will help you get started.

## 🌟 How to Contribute

### Ways to Contribute
- 🐛 Report bugs
- ✨ Suggest new features
- 📝 Improve documentation
- 🔧 Fix issues
- 🎨 Enhance UI/UX
- ⚡ Optimize performance
- 🧪 Add tests

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/your-username/datalens-ai.git
cd datalens-ai
```

### 2. Set Up Development Environment

Run the setup script:
```bash
# Windows
setup.bat

# macOS/Linux
./setup.sh
```

Or set up manually:
```bash
# Backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding tests
- `perf/` - Performance improvements

## 💻 Development Workflow

### Backend Development (Python/Flask)

**File Structure:**
```
├── flask_app.py              # Main Flask server (includes chart generation)
├── langchain_utils.py        # LangChain integration
└── config.py                 # App configuration
```

**Coding Standards:**
- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and under 50 lines
- Use meaningful variable names

**Example:**
```python
def process_query(query: str, csv_data: dict) -> dict:
    """
    Process a natural language query against CSV data.
    
    Args:
        query: User's natural language question
        csv_data: Dictionary with 'columns' and 'data' keys
        
    Returns:
        Dictionary with 'response' and optional 'charts' keys
        
    Raises:
        ValueError: If csv_data is invalid
    """
    # Implementation
    pass
```

**Running Backend:**
```bash
source venv/bin/activate  # Windows: venv\Scripts\activate
python flask_app.py
```

### Frontend Development (React/Vite)

**File Structure:**
```
frontend/src/
├── components/
│   ├── Navbar.jsx
│   ├── Sidebar.jsx
│   ├── QueryBox.jsx
│   ├── ChartsGrid.jsx
│   └── ...
├── App.jsx
├── main.jsx
└── index.css
```

**Coding Standards:**
- Use functional components with hooks
- Keep components under 200 lines
- Extract reusable logic into custom hooks
- Use meaningful component and variable names
- Add PropTypes or TypeScript types

**Example Component:**
```jsx
import React from 'react';

/**
 * ChartCard - Displays a single chart visualization
 * @param {Object} props
 * @param {Object} props.chartData - Chart.js configuration
 * @param {string} props.title - Chart title
 */
const ChartCard = ({ chartData, title }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-4">
      <h3 className="text-xl font-bold mb-4">{title}</h3>
      <Chart data={chartData} />
    </div>
  );
};

export default ChartCard;
```

**Running Frontend:**
```bash
cd frontend
npm run dev
```

## 🧪 Testing

### Manual Testing Checklist

Before submitting a PR, test:

**Backend:**
- [ ] `/upload` endpoint with various CSV files
- [ ] `/query` endpoint with different queries
- [ ] Error handling (invalid files, bad queries)
- [ ] Response format matches API spec

**Frontend:**
- [ ] File upload works correctly
- [ ] Queries return proper responses
- [ ] Charts render correctly
- [ ] Error messages display properly
- [ ] Responsive on mobile/tablet/desktop
- [ ] Works in Chrome, Firefox, Safari

### Automated Tests (Future)

We welcome contributions that add:
- Unit tests for backend functions
- Integration tests for API endpoints
- Component tests for React components
- E2E tests for critical user flows

## 📝 Code Review Process

### Before Submitting

1. **Test Your Changes**
   - Run the app locally
   - Test all affected functionality
   - Check for console errors

2. **Code Quality**
   - Remove console.log statements
   - Fix linting errors: `npm run lint`
   - Format code consistently
   - Add comments for complex logic

3. **Documentation**
   - Update README.md if needed
   - Update API_REFERENCE.md for API changes
   - Add inline code comments
   - Update relevant documentation files

### Submitting a Pull Request

1. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add chart export functionality"
   ```

   Commit message format:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting)
   - `refactor:` - Code refactoring
   - `perf:` - Performance improvements
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

2. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill out the PR template

### PR Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
Describe how you tested your changes

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tested locally
```

## 🐛 Reporting Bugs

### Before Reporting

1. Check existing issues
2. Test with latest version
3. Verify it's not a configuration issue

### Bug Report Template

```markdown
**Describe the bug**
Clear description of what went wrong

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen

**Screenshots**
If applicable, add screenshots

**Environment:**
- OS: [e.g., Windows 10, macOS 12]
- Browser: [e.g., Chrome 120]
- Python version: [e.g., 3.10]
- Node version: [e.g., 18.0]

**Additional context**
Any other relevant information
```

## ✨ Suggesting Features

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed? Who will benefit?

**Proposed Solution**
How you envision this working

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Mockups, examples, or related features
```

## 🎨 UI/UX Guidelines

### Design Principles
- **Simple**: Keep the interface clean and intuitive
- **Responsive**: Work well on all screen sizes
- **Accessible**: Follow WCAG guidelines
- **Consistent**: Match existing design patterns

### Tailwind CSS
- Use utility classes for styling
- Follow existing color scheme
- Maintain consistent spacing
- Use responsive breakpoints

### Component Guidelines
- Make components reusable
- Keep styling in Tailwind classes
- Use semantic HTML
- Add proper ARIA labels

## 📚 Documentation

### What to Document
- New features and their usage
- API endpoint changes
- Configuration options
- Complex algorithms or logic
- Breaking changes

### Documentation Format
- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Keep README.md updated

## 🔒 Security

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead:
1. Email the maintainers directly
2. Provide detailed description
3. Include reproduction steps
4. Suggest potential fixes if possible

### Security Guidelines
- Never commit API keys or secrets
- Validate all user input
- Sanitize data before display
- Use environment variables for config
- Follow OWASP best practices

## 📋 Code of Conduct

### Our Standards
- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on what's best for the project
- Show empathy towards others
- Accept constructive criticism gracefully

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Unprofessional conduct

## 🏆 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## 📞 Getting Help

### Questions?
- Check existing documentation
- Search closed issues
- Ask in discussions section
- Contact maintainers

### Resources
- [README.md](README.md) - Complete documentation
- [API_REFERENCE.md](API_REFERENCE.md) - API details
- [QUICKSTART.md](QUICKSTART.md) - Getting started guide

## 📅 Development Roadmap

### Planned Features
- [ ] Export charts as images
- [ ] Save and share dashboards
- [ ] Multiple file upload
- [ ] User authentication
- [ ] Dashboard templates
- [ ] Real-time data updates
- [ ] Advanced chart customization
- [ ] Data transformation tools

Want to work on any of these? Let us know!

---

**Thank you for contributing to DataLens AI! 🚀**

Your contributions help make data analysis more accessible and powerful for everyone.
