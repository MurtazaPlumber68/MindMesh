# MindMesh
# RLLM CLI Assistant

Real-Time LLM-Enhanced CLI Assistant that converts natural language requests into safe, executable shell commands with intelligent safety analysis, command history management, and comprehensive statistics tracking.

## Overview

RLLM CLI Assistant bridges the gap between human language and shell commands, making the command line more accessible to users of all skill levels. Simply describe what you want to accomplish in plain English, and the assistant will generate the appropriate shell commands with detailed explanations, safety assessments, and execution tracking.

## Features

### Core Features
- 🤖 **Natural Language Processing**: Convert plain English requests into accurate shell commands
- 🔒 **Safety Analysis**: Built-in risk assessment with color-coded safety levels (low, medium, high, critical)
- 📊 **Command History**: Persistent history with execution tracking and timestamps
- 💡 **Detailed Explanations**: Every generated command includes a clear explanation of what it does
- 🎯 **Interactive Preview**: Review commands before execution with syntax highlighting
- 📁 **Script Export**: Bundle executed commands into downloadable shell scripts
- ⚡ **Real-time Interface**: Responsive web interface with smooth user experience
- 🔍 **Pattern Recognition**: Intelligent command generation based on common CLI patterns

### Advanced Features
- 📈 **Usage Statistics**: Track command generation, execution rates, and risk distribution
- 💾 **Data Persistence**: Auto-save command history to browser localStorage
- 📤 **Import/Export**: Export history as JSON or shell scripts, import previous sessions
- 🎨 **Enhanced UI**: Modern interface with dialogs, tabs, and toast notifications
- 🔧 **Settings Panel**: Manage preferences and data with dedicated settings interface
- 📱 **Responsive Design**: Optimized for desktop and mobile devices
- 🎯 **Smart Suggestions**: Contextual command examples and improved pattern matching

## Tech Stack

- **Frontend**: React 18 with TypeScript
- **Styling**: Tailwind CSS with shadcn/ui components
- **Icons**: Lucide React
- **Build Tool**: Vite
- **State Management**: React hooks and context
- **Notifications**: Sonner toast library
- **Data Storage**: Browser localStorage for persistence
- **UI Components**: Custom components built on Radix UI primitives

## Installation

### Prerequisites

- Node.js 18.0 or higher
- npm or yarn package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rllm-cli-assistant
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open in browser**
   Navigate to `http://localhost:8080` to access the application

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Usage

### Basic Usage

#### Command Generation
1. **Enter Natural Language Commands**
   - Type what you want to accomplish in plain English
   - Examples: "list all files", "create a new folder called projects", "check disk space"

2. **Review Generated Commands**
   - Each command comes with a detailed explanation
   - Safety level is indicated with color-coded badges
   - Review the command before executing

3. **Execute Commands**
   - Click the "Execute" button to mark commands as executed
   - Commands are tracked in your session history

4. **Export Scripts**
   - Bundle all executed commands into a downloadable shell script
   - Perfect for creating reusable automation scripts

#### Advanced Features
5. **View Statistics**
   - Click the "Stats" button to see usage analytics
   - Track total commands, execution rates, and risk distribution

6. **Manage Data**
   - Use the "Settings" button to access data management
   - Export command history as JSON or shell scripts
   - Import previous command sessions
   - Configure application preferences


### Example Commands

Try these natural language requests:

- "list all files including hidden ones"
- "create a new directory called workspace"
- "show current directory"
- "check git status"
- "find files larger than 100MB"
- "show disk usage"
- "monitor system resources"
- "backup important files"
- "search for text in files"
- "check network connectivity"
- "list running processes"
- "show environment variables"
- "check listening ports"
- "kill a process"

### Safety Levels

- **🟢 Low Risk**: File listing, navigation, viewing commands
- **🟡 Medium Risk**: File creation, basic system operations
- **🟠 High Risk**: System modifications, process management
- **🔴 Critical Risk**: Destructive operations, dangerous commands

All commands include detailed safety warnings and explanations to help users understand potential risks.

## Development

### Project Structure

```
src/
├── components/
│   ├── CLIAssistant.tsx    # Main CLI interface component with full functionality
│   └── ui/                 # Reusable UI components
├── pages/
│   └── Index.tsx          # Landing page
├── lib/
│   └── utils.ts           # Utility functions
└── styles/
    └── index.css          # Global styles and Tailwind config
├── hooks/                 # Custom React hooks
└── nav-items.tsx         # Navigation configuration
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking
- `npm test` - Run tests (placeholder)

### Code Style

This project uses:
- TypeScript for type safety
- ESLint for code linting
- Prettier for code formatting
- Sonner for toast notifications
- Tailwind CSS for styling

## Testing

Currently, the project uses manual testing. To test the application:

1. Start the development server
2. Test various natural language inputs with expanded command patterns
3. Verify command generation accuracy
4. Check safety level assignments
5. Test command history and export functionality

### Future Testing Plans

- Unit tests with Jest and React Testing Library
- Component testing for UI interactions
- Integration tests for localStorage persistence
- Toast notification testing
- Integration tests for command generation
- E2E tests with Playwright
- Safety validation tests

## Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines

- Write clear, descriptive commit messages
- Follow existing code style and conventions
- Add TypeScript types for all new code
- Test your changes thoroughly
- Update documentation as needed

### Code Standards

- Use TypeScript for all new code
- Follow React best practices
- Use functional components with hooks
- Implement proper error handling
- Add toast notifications for user feedback
- Maintain localStorage data persistence
- Write self-documenting code with clear variable names

## Roadmap

### Planned Features

- [ ] **LLM Integration**: Connect to OpenAI GPT-4 or local models
- [ ] **Real-time Command Execution**: Execute commands directly in the browser (with safety restrictions)
- [ ] **Advanced Safety**: Enhanced pattern detection and validation
- [ ] **Command Templates**: Pre-built command libraries for common tasks
- [ ] **User Profiles**: Personalized command history and preferences
- [ ] **Collaboration**: Team sharing and command libraries
- [ ] **Plugin System**: Extensible architecture for custom commands
- [ ] **Mobile Support**: Enhanced mobile interface
- [ ] **Offline Mode**: Local command generation capabilities
- [ ] **Cloud Sync**: Synchronize command history across devices
- [ ] **Team Workspaces**: Shared command libraries and collaboration

### Technical Improvements

- [ ] Comprehensive test suite
- Performance optimizations
- Accessibility improvements
- Internationalization support
- Advanced statistics and analytics
- Command search and filtering
- Keyboard shortcuts and hotkeys
- Dark mode theme
- Command search and filtering

## Security Considerations

- Commands are generated locally without server-side execution
- Safety analysis helps prevent dangerous operations
- All data is stored locally in browser localStorage
- No actual shell execution occurs in the web interface
- User data remains in browser session storage

## Support

- 📖 Documentation: Check this README and inline code comments
- 🐛 Issues: Report bugs via GitHub Issues
- 💡 Feature Requests: Submit enhancement requests via GitHub Issues
- 📧 Contact: Open an issue for general questions

## Acknowledgments

- Built with React 18 and modern web technologies
- UI components powered by Radix UI and shadcn/ui
- Icons provided by Lucide React
- Toast notifications by Sonner
- Styled with Tailwind CSS