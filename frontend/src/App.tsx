import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/sidebar/Sidebar';
import { ChatWorkspace } from './components/chat/ChatWorkspace';
import { ArtifactViewer } from './components/artifacts/ArtifactViewer';
import { Modal } from './components/ui/Modal';
import {
  fetchConversations,
  fetchConversation,
  renameConversation,
  deleteConversation,
  sendChatMessage,
  fetchModels,
  setActiveProvider,
  fetchHealth,
} from './services/api';
import {
  ConversationSummary,
  ConversationDetail,
  ModelOption,
  Artifact,
  HealthStatus,
} from './types';

export const App: React.FC = () => {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [currentConversation, setCurrentConversation] = useState<ConversationDetail | null>(null);
  const [models, setModels] = useState<ModelOption[]>([]);
  const [activeProvider, setActiveProviderState] = useState<string>('ollama');
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [isArtifactOpen, setIsArtifactOpen] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [activeNavTab, setActiveNavTab] = useState<string>('dashboard');

  // Modals state
  const [renameModal, setRenameModal] = useState<{ isOpen: boolean; id: string; title: string }>({
    isOpen: false,
    id: '',
    title: '',
  });
  const [deleteModal, setDeleteModal] = useState<{ isOpen: boolean; id: string; title: string }>({
    isOpen: false,
    id: '',
    title: '',
  });

  // Initial Load
  useEffect(() => {
    loadHealthAndModels();
    loadConversations();
  }, []);

  const loadHealthAndModels = async () => {
    try {
      const [h, m] = await Promise.all([fetchHealth(), fetchModels()]);
      setHealth(h);
      setModels(m);

      const activeIsAvailable = m.some((mod) => mod.provider === h.active_provider && mod.is_available);
      if (h.active_provider && activeIsAvailable) {
        setActiveProviderState(h.active_provider);
      } else {
        const firstAvailable = m.find((mod) => mod.is_available);
        if (firstAvailable) {
          setActiveProviderState(firstAvailable.provider);
        } else if (h.active_provider) {
          setActiveProviderState(h.active_provider);
        }
      }
    } catch (err) {
      console.warn('Initial status fetch error:', err);
    }
  };

  const loadConversations = async () => {
    try {
      const list = await fetchConversations();
      setConversations(list);
    } catch (err) {
      console.error('Error loading conversations:', err);
    }
  };

  // Load selected conversation
  useEffect(() => {
    if (!activeConversationId) {
      setCurrentConversation(null);
      setActiveArtifact(null);
      return;
    }
    const loadDetail = async () => {
      try {
        const detail = await fetchConversation(activeConversationId);
        setCurrentConversation(detail);
        if (detail.artifacts && detail.artifacts.length > 0) {
          const latestArtifact = detail.artifacts[detail.artifacts.length - 1];
          setActiveArtifact(latestArtifact);
        }
      } catch (err) {
        console.error('Failed to load conversation detail:', err);
      }
    };
    loadDetail();
  }, [activeConversationId]);

  const handleNewChat = () => {
    setActiveConversationId(null);
    setCurrentConversation(null);
    setActiveArtifact(null);
    setIsArtifactOpen(false);
    setActiveNavTab('dashboard');
  };

  const handleSelectConversation = (id: string) => {
    setActiveConversationId(id);
    setActiveNavTab('history');
  };

  const handleSendMessage = async (messageText: string) => {
    setIsLoading(true);
    try {
      const response = await sendChatMessage({
        conversationId: activeConversationId,
        message: messageText,
        provider: activeProvider,
      });

      // Update active ID if this was a new conversation
      if (!activeConversationId) {
        setActiveConversationId(response.conversation_id);
      }

      // Reload detail
      const updated = await fetchConversation(response.conversation_id);
      setCurrentConversation(updated);
      await loadConversations();

      // If an artifact was produced, display it in the viewer
      if (response.artifact) {
        setActiveArtifact(response.artifact);
        setIsArtifactOpen(true);
      }
    } catch (err: any) {
      alert(`Error sending message: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectProvider = async (provider: string) => {
    setActiveProviderState(provider);
    try {
      await setActiveProvider(provider);
    } catch (err) {
      console.error('Failed to set active provider on backend:', err);
    }
  };

  // Rename Actions
  const openRenameModal = (id: string, currentTitle: string) => {
    setRenameModal({ isOpen: true, id, title: currentTitle });
  };

  const handleConfirmRename = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!renameModal.title.trim()) return;
    try {
      await renameConversation(renameModal.id, renameModal.title.trim());
      await loadConversations();
      if (currentConversation && currentConversation.id === renameModal.id) {
        setCurrentConversation({ ...currentConversation, title: renameModal.title.trim() });
      }
      setRenameModal({ isOpen: false, id: '', title: '' });
    } catch (err: any) {
      alert(`Failed to rename: ${err.message}`);
    }
  };

  // Delete Actions
  const openDeleteModal = (id: string, title: string) => {
    setDeleteModal({ isOpen: true, id, title });
  };

  const handleConfirmDelete = async () => {
    try {
      await deleteConversation(deleteModal.id);
      await loadConversations();
      if (activeConversationId === deleteModal.id) {
        handleNewChat();
      }
      setDeleteModal({ isOpen: false, id: '', title: '' });
    } catch (err: any) {
      alert(`Failed to delete: ${err.message}`);
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#EDF2FA]">
      {/* 1. Left Sidebar (TaskFlow AI Navigation) */}
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        health={health}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        onRenameConversation={openRenameModal}
        onDeleteConversation={openDeleteModal}
        activeNavTab={activeNavTab}
        onSelectNavTab={(tab) => {
          setActiveNavTab(tab);
          if (tab === 'dashboard') {
            handleNewChat();
          }
        }}
      />

      {/* 2. Main Workspace */}
      <div className="flex-1 flex overflow-hidden">
        <ChatWorkspace
          conversation={currentConversation}
          models={models}
          activeProvider={activeProvider}
          onSelectProvider={handleSelectProvider}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          onRenameTitle={() => {
            if (currentConversation) {
              openRenameModal(currentConversation.id, currentConversation.title);
            }
          }}
          activeArtifact={activeArtifact}
          isArtifactOpen={isArtifactOpen}
          onToggleArtifact={() => setIsArtifactOpen(!isArtifactOpen)}
        />

        {/* 3. Artifact Viewer Panel */}
        {isArtifactOpen && (
          <ArtifactViewer
            artifact={activeArtifact}
            onClose={() => setIsArtifactOpen(false)}
          />
        )}
      </div>

      {/* Rename Modal */}
      <Modal
        isOpen={renameModal.isOpen}
        onClose={() => setRenameModal({ isOpen: false, id: '', title: '' })}
        title="Rename Conversation"
      >
        <form onSubmit={handleConfirmRename} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Conversation Title
            </label>
            <input
              type="text"
              value={renameModal.title}
              onChange={(e) => setRenameModal({ ...renameModal, title: e.target.value })}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-violet-500"
              autoFocus
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setRenameModal({ isOpen: false, id: '', title: '' })}
              className="px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-3.5 py-1.5 text-xs font-semibold text-white bg-violet-600 hover:bg-violet-700 rounded-lg transition-colors shadow-sm"
            >
              Save Title
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteModal.isOpen}
        onClose={() => setDeleteModal({ isOpen: false, id: '', title: '' })}
        title="Delete Conversation"
      >
        <div className="space-y-4">
          <p className="text-xs text-slate-600 leading-relaxed">
            Are you sure you want to delete <span className="font-semibold text-slate-800">"{deleteModal.title}"</span>?
            This will permanently remove all messages and generated artifacts in this session.
          </p>
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setDeleteModal({ isOpen: false, id: '', title: '' })}
              className="px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleConfirmDelete}
              className="px-3.5 py-1.5 text-xs font-semibold text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors shadow-sm"
            >
              Delete Conversation
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default App;
