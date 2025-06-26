
import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Terminal, Send, History, Download, AlertTriangle, Zap } from 'lucide-react';

interface CommandEntry {
  id: string;
  query: string;
  command: string;
  explanation: string;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  timestamp: Date;
  executed: boolean;
}

export default function CLIAssistant() {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<CommandEntry[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [history]);

  const generateCommand = async (query: string): Promise<Omit<CommandEntry, 'id' | 'timestamp' | 'executed'>> => {
    // Simulate LLM processing delay
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const lowerQuery = query.toLowerCase();
    
    // Enhanced command generation with more patterns
    if (lowerQuery.includes('list') && (lowerQuery.includes('file') || lowerQuery.includes('directory'))) {
      return {
        query,
        command: lowerQuery.includes('hidden') ? 'ls -la' : 'ls -l',
        explanation: lowerQuery.includes('hidden') 
          ? 'Lists all files and directories including hidden ones with detailed information (permissions, ownership, size, modification date).'
          : 'Lists files and directories with detailed information including permissions, ownership, and timestamps.',
        riskLevel: 'low'
      };
    } else if (lowerQuery.includes('create') && (lowerQuery.includes('folder') || lowerQuery.includes('directory'))) {
      const folderName = query.match(/(?:folder|directory).*?(?:called|named)\s+(\w+)/i)?.[1] || 
                        query.match(/create.*?(\w+)/i)?.[1] || 'new_folder';
      return {
        query,
        command: `mkdir "${folderName}"`,
        explanation: `Creates a new directory named '${folderName}' in the current location. The directory will be created with default permissions.`,
        riskLevel: 'low'
      };
    } else if (lowerQuery.includes('disk') && lowerQuery.includes('space')) {
      return {
        query,
        command: 'df -h',
        explanation: 'Shows disk usage statistics in human-readable format, displaying available and used space for all mounted filesystems.',
        riskLevel: 'low'
      };
    } else if (lowerQuery.includes('current') && lowerQuery.includes('directory')) {
      return {
        query,
        command: 'pwd',
        explanation: 'Prints the full path of the current working directory.',
        riskLevel: 'low'
      };
    } else if (lowerQuery.includes('git') && lowerQuery.includes('status')) {
      return {
        query,
        command: 'git status',
        explanation: 'Shows the working tree status including staged files, unstaged changes, and untracked files in the Git repository.',
        riskLevel: 'low'
      };
    } else if (lowerQuery.includes('find') && lowerQuery.includes('large')) {
      return {
        query,
        command: 'find . -type f -size +100M -exec ls -lh {} \\;',
        explanation: 'Finds files larger than 100MB in the current directory and subdirectories, displaying their sizes in human-readable format.',
        riskLevel: 'medium'
      };
    } else if (lowerQuery.includes('memory') || lowerQuery.includes('ram')) {
      return {
        query,
        command: 'free -h',
        explanation: 'Displays system memory usage including total, used, free, and available memory in human-readable format.',
        riskLevel: 'low'
      };
    } else if (lowerQuery.includes('process') && lowerQuery.includes('list')) {
      return {
        query,
        command: 'ps aux',
        explanation: 'Lists all running processes with detailed information including CPU usage, memory usage, and process IDs.',
        riskLevel: 'medium'
      };
    } else if (lowerQuery.includes('remove') || lowerQuery.includes('delete')) {
      const isRecursive = lowerQuery.includes('folder') || lowerQuery.includes('directory');
      return {
        query,
        command: isRecursive ? 'rm -rf target_directory/' : 'rm target_file',
        explanation: `${isRecursive ? 'Recursively removes' : 'Removes'} the specified ${isRecursive ? 'directory and all its contents' : 'file'}. ⚠️ WARNING: This operation is irreversible and will permanently delete data.`,
        riskLevel: 'high'
      };
    } else if (lowerQuery.includes('permission') || lowerQuery.includes('chmod')) {
      return {
        query,
        command: 'chmod 755 filename',
        explanation: 'Changes file permissions to 755 (read/write/execute for owner, read/execute for group and others). Modifying permissions can affect system security.',
        riskLevel: 'medium'
      };
    } else {
      return {
        query,
        command: `# Generated command for: "${query}"`,
        explanation: 'This is a demonstration command. In production, this would be generated by an advanced LLM model that understands your specific request and generates the appropriate shell command with proper safety analysis.',
        riskLevel: 'medium'
      };
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    setIsLoading(true);
    try {
      const result = await generateCommand(input);
      const newEntry: CommandEntry = {
        ...result,
        id: Date.now().toString(),
        timestamp: new Date(),
        executed: false
      };

      setHistory(prev => [...prev, newEntry]);
      setInput('');
    } catch (error) {
      console.error('Error generating command:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const executeCommand = (id: string) => {
    setHistory(prev => 
      prev.map(entry => 
        entry.id === id ? { ...entry, executed: true } : entry
      )
    );
  };

  const exportScript = () => {
    const executedCommands = history.filter(entry => entry.executed);
    const script = executedCommands
      .map(entry => `# ${entry.query}\n# ${entry.explanation}\n${entry.command}`)
      .join('\n\n');
    
    const fullScript = `#!/bin/bash
# RLLM CLI Assistant - Generated Script
# Created: ${new Date().toISOString()}
# Commands: ${executedCommands.length}

${script}`;
    
    const blob = new Blob([fullScript], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `rllm-script-${Date.now()}.sh`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getRiskIcon = (riskLevel: string) => {
    if (riskLevel === 'high' || riskLevel === 'critical') {
      return <AlertTriangle className="h-3 w-3 mr-1" />;
    }
    return null;
  };

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <Card className="border-0 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 border-b">
          <CardTitle className="flex items-center gap-3 text-2xl">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Terminal className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-gray-900">RLLM CLI Assistant</h1>
              <p className="text-sm font-normal text-gray-600 mt-1">
                Transform natural language into safe, executable shell commands
              </p>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Describe what you want to do... (e.g., 'list all files', 'create a new folder called projects')"
                  disabled={isLoading}
                  className="pr-12 h-12 text-base"
                />
                {isLoading && (
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <Zap className="h-4 w-4 animate-pulse text-blue-500" />
                  </div>
                )}
              </div>
              <Button 
                type="submit" 
                disabled={isLoading || !input.trim()}
                className="h-12 px-6"
                size="lg"
              >
                <Send className="h-4 w-4 mr-2" />
                {isLoading ? 'Generating...' : 'Generate'}
              </Button>
            </div>
          </form>

          <div className="flex flex-wrap gap-3 mt-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setHistory([])}
              disabled={history.length === 0}
              className="h-9"
            >
              <History className="h-4 w-4 mr-2" />
              Clear History ({history.length})
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={exportScript}
              disabled={history.filter(h => h.executed).length === 0}
              className="h-9"
            >
              <Download className="h-4 w-4 mr-2" />
              Export Script ({history.filter(h => h.executed).length})
            </Button>
          </div>

          <ScrollArea className="h-[500px] w-full border rounded-lg mt-6 bg-gray-50/50" ref={scrollRef}>
            {history.length === 0 ? (
              <div className="text-center py-12 px-6">
                <div className="mx-auto mb-6 w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                  <Terminal className="h-8 w-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to assist you</h3>
                <p className="text-gray-600 mb-6">Try describing what you want to accomplish in natural language</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto text-sm">
                  <div className="bg-white p-3 rounded-lg border border-gray-200">
                    <span className="text-gray-500">"</span>list all files including hidden ones<span className="text-gray-500">"</span>
                  </div>
                  <div className="bg-white p-3 rounded-lg border border-gray-200">
                    <span className="text-gray-500">"</span>create a folder called workspace<span className="text-gray-500">"</span>
                  </div>
                  <div className="bg-white p-3 rounded-lg border border-gray-200">
                    <span className="text-gray-500">"</span>check current directory<span className="text-gray-500">"</span>
                  </div>
                  <div className="bg-white p-3 rounded-lg border border-gray-200">
                    <span className="text-gray-500">"</span>show git repository status<span className="text-gray-500">"</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-4 space-y-6">
                {history.map((entry, index) => (
                  <div key={entry.id} className="bg-white rounded-lg border border-gray-200 p-5 shadow-sm">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-3">
                          <span className="text-sm font-medium text-gray-700">Query:</span>
                          <span className="text-sm text-gray-900 bg-gray-50 px-2 py-1 rounded">
                            {entry.query}
                          </span>
                        </div>
                        
                        <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm mb-4 overflow-x-auto">
                          <div className="flex items-center gap-2 mb-2 text-gray-500">
                            <Terminal className="h-3 w-3" />
                            <span className="text-xs">shell</span>
                          </div>
                          <code>{entry.command}</code>
                        </div>
                        
                        <p className="text-sm text-gray-700 mb-4 leading-relaxed">
                          {entry.explanation}
                        </p>
                        
                        <div className="flex items-center gap-3 flex-wrap">
                          <Badge className={`${getRiskColor(entry.riskLevel)} border`}>
                            {getRiskIcon(entry.riskLevel)}
                            {entry.riskLevel} risk
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {entry.timestamp.toLocaleString()}
                          </span>
                          {entry.executed && (
                            <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50">
                              ✓ Executed
                            </Badge>
                          )}
                        </div>
                      </div>
                      
                      <Button
                        size="sm"
                        variant={entry.executed ? "outline" : "default"}
                        onClick={() => executeCommand(entry.id)}
                        disabled={entry.executed}
                        className="ml-4 shrink-0"
                      >
                        {entry.executed ? "Executed" : "Execute"}
                      </Button>
                    </div>
                    
                    {index < history.length - 1 && <Separator className="mt-5" />}
                  </div>
                ))}
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
