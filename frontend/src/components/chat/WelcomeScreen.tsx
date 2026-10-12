import React from 'react';
import { Sparkles, TrendingUp, Compass, FileText, Layout } from 'lucide-react';

interface WelcomeScreenProps {
  onSelectPrompt: (prompt: string) => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSelectPrompt }) => {
  const examplePrompts = [
    {
      title: 'B2B Growth & AI Loops',
      description: 'How does Elena Verna reinvent growth loops for AI-native products at Lovable?',
      icon: TrendingUp,
      prompt: 'How does Elena Verna reinvent growth loops for AI-native companies, and what is her playbook on Lovable reaching $200M ARR?',
      color: 'text-violet-600 bg-violet-50',
    },
    {
      title: 'Product-Market Fit & Strategy',
      description: 'What are the counter-intuitive signals of true PMF according to Marc Andreessen and Peter Sellis?',
      icon: Compass,
      prompt: 'What are the counter-intuitive signs of true Product-Market Fit according to Marc Andreessen and Peter Sellis in their podcast interviews?',
      color: 'text-blue-600 bg-blue-50',
    },
    {
      title: 'Ship 30 for 30 Essay',
      description: 'Generate an executive Atomic Essay (~1,250 words) on why retention eats acquisition.',
      icon: FileText,
      prompt: 'Write a Ship 30 for 30 essay on why retention eats acquisition in modern SaaS, grounded in Lenny’s podcast transcripts.',
      color: 'text-amber-600 bg-amber-50',
    },
    {
      title: 'Interactive Webpage Artifact',
      description: 'Generate an interactive HTML/CSS viral coefficient and growth loop calculator.',
      icon: Layout,
      prompt: 'Generate an interactive HTML/CSS webpage component with a modern calculator for calculating viral factor (K) and SaaS retention cohorts.',
      color: 'text-emerald-600 bg-emerald-50',
    },
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 max-w-3xl mx-auto text-center">
      <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-violet-600 to-indigo-500 text-white flex items-center justify-center shadow-lg mb-4">
        <Sparkles className="w-6 h-6" />
      </div>

      <h2 className="text-xl sm:text-2xl font-bold text-slate-800 tracking-tight mb-2">
        The Lenny Growth Assistant
      </h2>
      <p className="text-xs sm:text-sm text-slate-500 max-w-lg mb-8 leading-relaxed">
        Grounded in 50+ transcripts from Lenny’s Podcast. Ask tactical product questions,
        generate Ship 30 for 30 essays, or build interactive web artifacts.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left">
        {examplePrompts.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              onClick={() => onSelectPrompt(item.prompt)}
              className="p-3.5 bg-white hover:bg-slate-50 border border-slate-200/90 rounded-xl shadow-sm hover:shadow transition-all group flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <div className={`p-1.5 rounded-lg ${item.color}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <h3 className="text-xs font-semibold text-slate-800 group-hover:text-violet-600 transition-colors">
                    {item.title}
                  </h3>
                </div>
                <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
                  {item.description}
                </p>
              </div>
              <span className="text-[10px] text-violet-600 font-medium mt-3 flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
                Ask this →
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
