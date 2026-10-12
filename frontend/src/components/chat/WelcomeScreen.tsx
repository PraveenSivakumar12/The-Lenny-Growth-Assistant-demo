import React, { useState } from 'react';
import {
  ArrowUp,
  Plus,
  ArrowDown,
  Workflow,
  Cpu,
  BarChart2,
  Lightbulb,
  CalendarCheck,
} from 'lucide-react';

interface WelcomeScreenProps {
  onSelectPrompt: (prompt: string) => void;
}

function getTimeGreeting(): string {
  const hour = new Date().getHours();
  if (hour >= 5 && hour < 12) return 'Good Morning';
  if (hour >= 12 && hour < 17) return 'Good Afternoon';
  return 'Good Evening';
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSelectPrompt }) => {
  const [inputVal, setInputVal] = useState('');
  const greeting = getTimeGreeting();

  const quickActions = [
    {
      label: 'Create AI Flow',
      icon: Workflow,
      prompt: "Design an end-to-end B2B PLG growth loop and automated onboarding flow based on Lenny's podcast transcripts.",
    },
    {
      label: 'Build Automation',
      icon: Cpu,
      prompt: 'How can we automate product retention analysis and churn alert loops for our SaaS tier?',
    },
    {
      label: 'Analyze Process',
      icon: BarChart2,
      prompt: "Analyze Elena Verna's acquisition loops vs Lovable's viral loops and explain key metrics.",
    },
    {
      label: 'Get AI Suggestion',
      icon: Lightbulb,
      prompt: "What are the top 3 counter-intuitive product growth principles shared across Lenny's podcast guests?",
    },
    {
      label: 'AI Task Planner',
      icon: CalendarCheck,
      prompt: 'Write an executive Ship 30 for 30 essay outline and execution plan for launching product-led sales.',
    },
  ];

  const handleSubmit = () => {
    if (inputVal.trim()) {
      onSelectPrompt(inputVal.trim());
      setInputVal('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4 sm:px-8 py-8 w-full max-w-4xl mx-auto text-center select-none">
      {/* Glowing Gradient Orb */}
      <div className="relative mb-6">
        <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-gradient-to-tr from-violet-600 via-fuchsia-400 to-indigo-300 shadow-[0_0_50px_rgba(168,85,247,0.45)] flex items-center justify-center p-1 transition-transform hover:scale-105 duration-300">
          <div className="w-full h-full rounded-full bg-gradient-to-br from-white/30 via-violet-300/20 to-transparent backdrop-blur-sm flex items-center justify-center border border-white/40">
            <div className="w-8 h-8 rounded-full bg-white/40"></div>
          </div>
        </div>
      </div>

      {/* Time-based greeting — no name */}
      <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-800 tracking-tight mb-2">
        {greeting} 👋
      </h1>
      <h2 className="text-base sm:text-lg font-semibold text-slate-700 mb-1">
        Master your day with AI automation
      </h2>
      <p className="text-xs sm:text-sm text-slate-500 max-w-md mb-8">
        Experience the next level of productivity. Let AI handle the busywork grounded in Lenny's Growth Intelligence.
      </p>

      {/* Hero Prompt Input Card */}
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.06)] border border-slate-200/80 p-3 sm:p-4 mb-8 transition-all hover:shadow-[0_12px_40px_rgb(0,0,0,0.09)]">
        <div className="text-left mb-3">
          <input
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask Anything"
            className="w-full text-sm sm:text-base font-normal text-slate-800 placeholder-slate-400 outline-none bg-transparent px-1 py-1"
          />
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-slate-100">
          <div className="flex items-center gap-2 text-slate-400">
            <button
              type="button"
              onClick={() => onSelectPrompt('Generate an interactive HTML/CSS growth calculator component')}
              className="p-1.5 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
              title="Insert prompt template"
            >
              <Plus className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={() => onSelectPrompt('Write a Ship 30 for 30 essay on SaaS growth')}
              className="p-1.5 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
              title="Insert prompt"
            >
              <ArrowDown className="w-4 h-4" />
            </button>
          </div>

          <button
            type="button"
            onClick={handleSubmit}
            disabled={!inputVal.trim()}
            className={`w-9 h-9 rounded-xl flex items-center justify-center text-white transition-all shadow-sm ${
              inputVal.trim()
                ? 'bg-violet-600 hover:bg-violet-700 cursor-pointer'
                : 'bg-violet-500/60 cursor-not-allowed'
            }`}
            title="Submit question"
          >
            <ArrowUp className="w-4 h-4 stroke-[2.5]" />
          </button>
        </div>
      </div>

      {/* Quick Action Pills */}
      <div className="w-full max-w-2xl text-left">
        <div className="text-xs font-bold text-slate-700 mb-3 px-1">Quick Action</div>
        <div className="flex flex-wrap items-center gap-2">
          {quickActions.map((action, idx) => {
            const Icon = action.icon;
            return (
              <button
                key={idx}
                onClick={() => onSelectPrompt(action.prompt)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white/90 hover:bg-white text-slate-700 hover:text-violet-700 border border-slate-200/80 hover:border-violet-300 rounded-xl text-xs font-medium shadow-sm hover:shadow transition-all"
              >
                <Icon className="w-3.5 h-3.5 text-slate-400" />
                <span>{action.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
