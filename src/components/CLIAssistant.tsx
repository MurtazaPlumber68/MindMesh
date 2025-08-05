import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { useToast } from '../hooks/use-toast';
import { 
  Terminal, 
  Play, 
  Download, 
  History, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  BarChart3,
  Settings,
  Upload,
  Trash2,
  Copy
} from 'lucide-react';

interface Command {
  id: string;
  prompt: string;
  command: string;
  explanation: string;
  riskLevel: 'low' | 'medium' | 'high';
  timestamp: Date;
  executed: boolean;
}

interface Statistics {
  totalCommands: number;
  executedCommands: number;
  riskDistribution: {
    low: number;
    medium: number;
    high: number;
  };
}

const CLIAssistant: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [currentCommand, setCurrentCommand] = useState<Command | null>(null);
  const [history, setHistory] = useState<Command[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [statistics, setStatistics] = useState<Statistics>({
    totalCommands: 0,
    executedCommands: 0,
    riskDistribution: { low: 0, medium: 0, high: 0 }
  });
  const { toast } = useToast();

  // Load data from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('cli-assistant-history');
    if (savedHistory) {
      try {
        const parsedHistory = JSON.parse(savedHistory).map((cmd: any) => ({
          ...cmd,
          timestamp: new Date(cmd.timestamp)
        }));
        setHistory(parsedHistory);
        updateStatistics(parsedHistory);
      } catch (error) {
        console.error('Failed to load history:', error);
      }
    }
  }, []);

  // Save to localStorage whenever history changes
  useEffect(() => {
    if (history.length > 0) {
      localStorage.setItem('cli-assistant-history', JSON.stringify(history));
      updateStatistics(history);
    }
  }, [history]);

  const updateStatistics = (commands: Command[]) => {
    const stats: Statistics = {
      totalCommands: commands.length,
      executedCommands: commands.filter(cmd => cmd.executed).length,
      riskDistribution: {
        low: commands.filter(cmd => cmd.riskLevel === 'low').length,
        medium: commands.filter(cmd => cmd.riskLevel === 'medium').length,
        high: commands.filter(cmd => cmd.riskLevel === 'high').length
      }
    };
    setStatistics(stats);
  };

  const commandPatterns = [
    // File operations
    { pattern: /list.*files?|show.*directory|ls/, command: 'ls -la', risk: 'low' as const },
    { pattern: /create.*file|touch.*file/, command: 'touch filename.txt', risk: 'low' as const },
    { pattern: /copy.*file|cp/, command: 'cp source.txt destination.txt', risk: 'medium' as const },
    { pattern: /move.*file|mv/, command: 'mv oldname.txt newname.txt', risk: 'medium' as const },
    { pattern: /delete.*file|remove.*file|rm/, command: 'rm filename.txt', risk: 'high' as const },
    { pattern: /find.*file/, command: 'find . -name "*.txt"', risk: 'low' as const },
    
    // Directory operations
    { pattern: /create.*directory|mkdir/, command: 'mkdir new_directory', risk: 'low' as const },
    { pattern: /change.*directory|cd/, command: 'cd /path/to/directory', risk: 'low' as const },
    { pattern: /current.*directory|pwd/, command: 'pwd', risk: 'low' as const },
    
    // System information
    { pattern: /system.*info|uname/, command: 'uname -a', risk: 'low' as const },
    { pattern: /disk.*usage|df/, command: 'df -h', risk: 'low' as const },
    { pattern: /memory.*usage|free/, command: 'free -h', risk: 'low' as const },
    { pattern: /process.*list|ps/, command: 'ps aux', risk: 'low' as const },
    { pattern: /top.*processes|htop/, command: 'htop', risk: 'low' as const },
    
    // Network operations
    { pattern: /ping/, command: 'ping google.com', risk: 'low' as const },
    { pattern: /network.*status|netstat/, command: 'netstat -tuln', risk: 'low' as const },
    { pattern: /download.*file|wget|curl/, command: 'wget https://example.com/file.txt', risk: 'medium' as const },
    
    // Git operations
    { pattern: /git.*status/, command: 'git status', risk: 'low' as const },
    { pattern: /git.*add/, command: 'git add .', risk: 'medium' as const },
    { pattern: /git.*commit/, command: 'git commit -m "commit message"', risk: 'medium' as const },
    { pattern: /git.*push/, command: 'git push origin main', risk: 'medium' as const },
    { pattern: /git.*pull/, command: 'git pull origin main', risk: 'medium' as const },
    
    // Docker operations
    { pattern: /docker.*list|docker.*ps/, command: 'docker ps -a', risk: 'low' as const },
    { pattern: /docker.*run/, command: 'docker run -it ubuntu:latest /bin/bash', risk: 'medium' as const },
    { pattern: /docker.*stop/, command: 'docker stop container_name', risk: 'medium' as const },
    
    // Package management
    { pattern: /install.*package|apt.*install/, command: 'sudo apt install package_name', risk: 'high' as const },
    { pattern: /update.*system|apt.*update/, command: 'sudo apt update && sudo apt upgrade', risk: 'high' as const },
    
    // File permissions
    { pattern: /change.*permission|chmod/, command: 'chmod 755 filename', risk: 'medium' as const },
    { pattern: /change.*owner|chown/, command: 'sudo chown user:group filename', risk: 'high' as const },
    
    // Archive operations
    { pattern: /compress|tar.*create/, command: 'tar -czf archive.tar.gz directory/', risk: 'low' as const },
    { pattern: /extract|tar.*extract/, command: 'tar -xzf archive.tar.gz', risk: 'medium' as const },
    
    // Text processing
    { pattern: /search.*text|grep/, command: 'grep "search_term" filename.txt', risk: 'low' as const },
    { pattern: /count.*lines|wc/, command: 'wc -l filename.txt', risk: 'low' as const },
    { pattern: /sort.*file/, command: 'sort filename.txt', risk: 'low' as const },
  ];

  const generateCommand = async (userPrompt: string): Promise<Command> => {
    const lowerPrompt = userPrompt.toLowerCase();
    
    // Find matching pattern
    const match = commandPatterns.find(pattern => pattern.pattern.test(lowerPrompt));
    
    let command = 'echo "Command not recognized"';
    let riskLevel: 'low' | 'medium' | 'high' = 'low';
    let explanation = 'This command was not recognized by the pattern matcher.';
    
    if (match) {
      command = match.command;
      riskLevel = match.risk;
      
      // Generate explanation based on risk level
      switch (riskLevel) {
        case 'low':
          explanation = `This is a safe read-only command that will ${userPrompt.toLowerCase()}. It won't modify your system.`;
          break;
        case 'medium':
          explanation = `This command will ${userPrompt.toLowerCase()}. It may modify files or system state, so review it carefully before executing.`;
          break;
        case 'high':
          explanation = `⚠️ This is a potentially dangerous command that will ${userPrompt.toLowerCase()}. It can make significant system changes. Use with extreme caution!`;
          break;
      }
    }
    
    return {
      id: Date.now().toString(),
      prompt: userPrompt,
      command,
      explanation,
      riskLevel,
      timestamp: new Date(),
      executed: false
    };
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast({
        title: "Error",
        description: "Please enter a command description",
        variant: "destructive"
      });
      return;
    }

    setIsGenerating(true);
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const command = await generateCommand(prompt);
      setCurrentCommand(command);
      
      toast({
        title: "Command Generated",
        description: "Review the command before executing",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate command",
        variant: "destructive"
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExecute = () => {
    if (!currentCommand) return;

    const executedCommand = { ...currentCommand, executed: true };
    setHistory(prev => [executedCommand, ...prev]);
    
    toast({
      title: "Command Executed",
      description: "Command has been added to history",
    });
    
    // Clear current command
    setCurrentCommand(null);
    setPrompt('');
  };

  const exportHistory = () => {
    const dataStr = JSON.stringify(history, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'cli-assistant-history.json';
    link.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: "Export Complete",
      description: "History exported successfully",
    });
  };

  const exportScript = () => {
    const executedCommands = history.filter(cmd => cmd.executed);
    if (executedCommands.length === 0) {
      toast({
        title: "No Commands",
        description: "No executed commands to export",
        variant: "destructive"
      });
      return;
    }

    const script = `#!/bin/bash\n# Generated by CLI Assistant\n# Generated on: ${new Date().toISOString()}\n\n` +
      executedCommands.map(cmd => `# ${cmd.prompt}\n${cmd.command}`).join('\n\n');
    
    const blob = new Blob([script], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'cli-commands.sh';
    link.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: "Script Exported",
      description: "Shell script downloaded successfully",
    });
  };

  const clearHistory = () => {
    setHistory([]);
    localStorage.removeItem('cli-assistant-history');
    toast({
      title: "History Cleared",
      description: "All command history has been cleared",
    });
  };

  const copyCommand = (command: string) => {
    navigator.clipboard.writeText(command);
    toast({
      title: "Copied",
      description: "Command copied to clipboard",
    });
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case 'low': return <CheckCircle className="w-4 h-4" />;
      case 'medium': return <AlertTriangle className="w-4 h-4" />;
      case 'high': return <XCircle className="w-4 h-4" />;
      default: return <AlertTriangle className="w-4 h-4" />;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold flex items-center justify-center gap-2">
          <Terminal className="w-8 h-8" />
          CLI Assistant
        </h1>
        <p className="text-gray-600">
          Generate safe and reliable command-line instructions from natural language
        </p>
      </div>

      {/* Main Input Card */}
      <Card>
        <CardHeader>
          <CardTitle>Describe what you want to do</CardTitle>
          <CardDescription>
            Enter a natural language description and get the corresponding CLI command
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="e.g., list all files in current directory"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleGenerate()}
              className="flex-1"
            />
            <Button 
              onClick={handleGenerate} 
              disabled={isGenerating}
              className="px-6"
            >
              {isGenerating ? 'Generating...' : 'Generate'}
            </Button>
          </div>

          {/* Example prompts */}
          <div className="flex flex-wrap gap-2">
            <span className="text-sm text-gray-500">Try:</span>
            {[
              'list all files',
              'check disk usage',
              'find Python files',
              'show running processes'
            ].map((example) => (
              <Button
                key={example}
                variant="outline"
                size="sm"
                onClick={() => setPrompt(example)}
                className="text-xs"
              >
                {example}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Generated Command */}
      {currentCommand && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                Generated Command
                <Badge className={getRiskColor(currentCommand.riskLevel)}>
                  {getRiskIcon(currentCommand.riskLevel)}
                  {currentCommand.riskLevel} risk
                </Badge>
              </CardTitle>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => copyCommand(currentCommand.command)}
                >
                  <Copy className="w-4 h-4" />
                </Button>
                <Button onClick={handleExecute} className="flex items-center gap-2">
                  <Play className="w-4 h-4" />
                  Execute
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Command:</label>
              <div className="mt-1 p-3 bg-gray-900 text-green-400 rounded-md font-mono text-sm">
                {currentCommand.command}
              </div>
            </div>
            
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                {currentCommand.explanation}
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}

      {/* Statistics and History */}
      <div className="flex gap-4">
        {/* Statistics Dialog */}
        <Dialog>
          <DialogTrigger asChild>
            <Button variant="outline" className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Statistics
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Usage Statistics</DialogTitle>
              <DialogDescription>
                Overview of your CLI Assistant usage
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {statistics.totalCommands}
                  </div>
                  <div className="text-sm text-blue-800">Total Commands</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {statistics.executedCommands}
                  </div>
                  <div className="text-sm text-green-800">Executed</div>
                </div>
              </div>
              
              <div className="space-y-2">
                <h4 className="font-medium">Risk Distribution</h4>
                <div className="space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Low Risk</span>
                    <Badge className="bg-green-100 text-green-800">
                      {statistics.riskDistribution.low}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Medium Risk</span>
                    <Badge className="bg-yellow-100 text-yellow-800">
                      {statistics.riskDistribution.medium}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">High Risk</span>
                    <Badge className="bg-red-100 text-red-800">
                      {statistics.riskDistribution.high}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {/* Settings Dialog */}
        <Dialog>
          <DialogTrigger asChild>
            <Button variant="outline" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Settings
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Settings</DialogTitle>
              <DialogDescription>
                Manage your CLI Assistant preferences
              </DialogDescription>
            </DialogHeader>
            <Tabs defaultValue="export" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="export">Export/Import</TabsTrigger>
                <TabsTrigger value="data">Data Management</TabsTrigger>
              </TabsList>
              
              <TabsContent value="export" className="space-y-4">
                <div className="space-y-2">
                  <Button onClick={exportHistory} className="w-full flex items-center gap-2">
                    <Download className="w-4 h-4" />
                    Export History (JSON)
                  </Button>
                  <Button onClick={exportScript} className="w-full flex items-center gap-2">
                    <Download className="w-4 h-4" />
                    Export as Shell Script
                  </Button>
                </div>
              </TabsContent>
              
              <TabsContent value="data" className="space-y-4">
                <Button 
                  onClick={clearHistory} 
                  variant="destructive" 
                  className="w-full flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Clear All History
                </Button>
              </TabsContent>
            </Tabs>
          </DialogContent>
        </Dialog>
      </div>

      {/* Command History */}
      {history.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="w-5 h-5" />
              Command History ({history.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {history.map((cmd) => (
                <div key={cmd.id} className="border rounded-lg p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">{cmd.prompt}</span>
                    <div className="flex items-center gap-2">
                      <Badge className={getRiskColor(cmd.riskLevel)}>
                        {cmd.riskLevel}
                      </Badge>
                      {cmd.executed && (
                        <Badge className="bg-blue-100 text-blue-800">
                          executed
                        </Badge>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <code className="text-sm bg-gray-100 px-2 py-1 rounded flex-1 mr-2">
                      {cmd.command}
                    </code>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyCommand(cmd.command)}
                    >
                      <Copy className="w-3 h-3" />
                    </Button>
                  </div>
                  <div className="text-xs text-gray-500">
                    {cmd.timestamp.toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CLIAssistant;