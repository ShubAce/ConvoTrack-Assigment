import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
	MessageCircle,
	Send,
	Brain,
	BarChart3,
	TrendingUp,
	Target,
	FileText,
	CheckCircle,
	AlertCircle,
	Loader,
	X,
	ExternalLink,
	BookOpen,
	Menu,
	User,
	ChevronDown,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import axios from "axios";

// The base URL for your FastAPI backend
const API_BASE_URL = "http://localhost:8000";

function App() {
	// --- STATE MANAGEMENT ---
	const [messages, setMessages] = useState([]);
	const [inputValue, setInputValue] = useState("");
	const [isLoading, setIsLoading] = useState(false);
	const [apiStatus, setApiStatus] = useState("checking");
	// State to hold a history of all citations from the conversation
	const [citationHistory, setCitationHistory] = useState([]);
	const [isSidebarOpen, setIsSidebarOpen] = useState(false);
	// State to track the expanded source, needs to know both group and source index
	const [expandedSource, setExpandedSource] = useState(null); // e.g., { group: 0, source: 1 }
	const messagesEndRef = useRef(null);

	// --- CONFIGURATION ---
	const analysisTypes = [
		{ id: "default", name: "General Analysis", icon: Brain, color: "from-gray-500 to-gray-600", lightColor: "bg-gray-50 text-gray-700" },
		{ id: "strategic", name: "Strategic Analysis", icon: Target, color: "from-blue-500 to-blue-600", lightColor: "bg-blue-50 text-blue-700" },
		{ id: "trends", name: "Trend Analysis", icon: TrendingUp, color: "from-green-500 to-green-600", lightColor: "bg-green-50 text-green-700" },
		{
			id: "comparative",
			name: "Comparative Analysis",
			icon: BarChart3,
			color: "from-purple-500 to-purple-600",
			lightColor: "bg-purple-50 text-purple-700",
		},
		{
			id: "executive",
			name: "Executive Summary",
			icon: FileText,
			color: "from-orange-500 to-orange-600",
			lightColor: "bg-orange-50 text-orange-700",
		},
	];

	// --- EFFECTS ---
	useEffect(() => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	}, [messages, isLoading]);

	useEffect(() => {
		const checkApiHealth = async () => {
			try {
				await axios.get(`${API_BASE_URL}/health`);
				setApiStatus("connected");
			} catch (error) {
				setApiStatus("disconnected");
				console.error("API health check failed:", error);
			}
		};
		checkApiHealth();
	}, []);

	// --- HANDLERS ---
	const handleInputSubmit = async (e) => {
		e.preventDefault();
		if (!inputValue.trim() || isLoading) return;

		const userMessage = {
			id: Date.now(),
			type: "user",
			content: inputValue,
			timestamp: new Date(),
		};

		setMessages((prev) => [...prev, userMessage]);
		const currentInput = inputValue;
		setInputValue("");
		setIsLoading(true);

		try {
			const response = await axios.post(`${API_BASE_URL}/ask`, {
				question: currentInput,
			});

			const analysisType = analysisTypes.find((t) => t.id === response.data.analysis_type) || analysisTypes[0];

			const responseSources = response.data.sources || [];

			const botMessage = {
				id: Date.now() + 1,
				type: "bot",
				content: response.data.answer,
				sources: responseSources,
				confidence: response.data.confidence,
				analysisType: analysisType,
				timestamp: new Date(),
			};

			setMessages((prev) => [...prev, botMessage]);

			// If the response has sources, add them to the citation history
			if (responseSources.length > 0) {
				const newCitationGroup = {
					query: currentInput,
					sources: responseSources,
				};
				setCitationHistory((prev) => [...prev, newCitationGroup]);
				// Auto-expand the first source of the new group
				setExpandedSource({ group: citationHistory.length, source: 0 });
				if (window.innerWidth < 1024) {
					setIsSidebarOpen(true);
				}
			}
		} catch (error) {
			console.error("Failed to get response:", error);
			const errorMessage = {
				id: Date.now() + 1,
				type: "error",
				content: "Sorry, I encountered an error. Please check the API connection or try your question again.",
				timestamp: new Date(),
			};
			setMessages((prev) => [...prev, errorMessage]);
		} finally {
			setIsLoading(false);
		}
	};

	// --- UI COMPONENTS ---
	const StatusIndicator = ({ status }) => {
		const statusConfig = {
			checking: { icon: Loader, color: "text-amber-500", label: "Connecting..." },
			connected: { icon: CheckCircle, color: "text-green-500", label: "Online" },
			disconnected: { icon: AlertCircle, color: "text-red-500", label: "Offline" },
		};
		const config = statusConfig[status];
		const Icon = config.icon;
		return (
			<div className="flex items-center gap-2 text-sm">
				<Icon className={`w-4 h-4 ${config.color} ${status === "checking" ? "animate-spin" : ""}`} />
				<span className={`${config.color} font-medium hidden sm:block`}>{config.label}</span>
			</div>
		);
	};

	const Sidebar = () => (
		<div className="h-full w-full bg-white flex flex-col">
			<div className="p-4 sm:p-6 border-b flex items-center justify-between flex-shrink-0">
				<div className="flex items-center gap-3">
					<BookOpen className="w-5 h-5 text-gray-600" />
					<h3 className="font-semibold text-gray-900">Citation History</h3>
				</div>
				<button
					onClick={() => setIsSidebarOpen(false)}
					className="p-1 hover:bg-gray-100 rounded-lg lg:hidden"
				>
					<X className="w-5 h-5 text-gray-500" />
				</button>
			</div>
			<div className="flex-1 overflow-y-auto p-4 sm:p-6">
				{citationHistory.length > 0 ? (
					<div className="space-y-6">
						{citationHistory.map((citationGroup, groupIndex) => (
							<div
								key={groupIndex}
								className="space-y-4"
							>
								<div className="bg-blue-50 border border-blue-200 text-blue-800 rounded-lg p-3">
									<p className="text-xs font-semibold mb-1">Citations for query:</p>
									<p className="text-sm font-medium italic">"{citationGroup.query}"</p>
								</div>
								{citationGroup.sources.map((source, sourceIndex) => (
									<div
										key={sourceIndex}
										className="bg-gray-50 rounded-lg border border-gray-200 overflow-hidden"
									>
										<button
											onClick={() =>
												setExpandedSource(
													expandedSource?.group === groupIndex && expandedSource?.source === sourceIndex
														? null
														: { group: groupIndex, source: sourceIndex }
												)
											}
											className="w-full p-4 text-left flex items-center justify-between hover:bg-gray-100 transition-colors"
										>
											<div className="flex-1">
												<p className="text-sm font-semibold text-blue-700">Source {sourceIndex + 1}</p>
												<p className="text-xs text-gray-500 break-all mt-1">{source.url || "Internal Knowledge Base"}</p>
											</div>
											<ChevronDown
												className={`w-5 h-5 text-gray-500 transition-transform ${
													expandedSource?.group === groupIndex && expandedSource?.source === sourceIndex ? "rotate-180" : ""
												}`}
											/>
										</button>
										<AnimatePresence>
											{expandedSource?.group === groupIndex && expandedSource?.source === sourceIndex && (
												<motion.div
													initial={{ height: 0, opacity: 0 }}
													animate={{ height: "auto", opacity: 1 }}
													exit={{ height: 0, opacity: 0 }}
													className="overflow-hidden"
												>
													<div className="p-4 border-t border-gray-200 text-sm text-gray-800 bg-white space-y-3">
														<p className="font-semibold">Extracted Content:</p>
														<pre className="text-xs whitespace-pre-wrap font-sans bg-gray-100 p-3 rounded-md max-h-56 overflow-y-auto border">
															{source.content}
														</pre>
														{source.url && source.url !== "Unknown" && (
															<a
																href={source.url}
																target="_blank"
																rel="noopener noreferrer"
																className="p-1 mt-2 inline-flex items-center gap-1.5 text-blue-600 hover:underline text-xs font-medium"
															>
																<ExternalLink className="w-3 h-3" /> Visit Original Source
															</a>
														)}
													</div>
												</motion.div>
											)}
										</AnimatePresence>
									</div>
								))}
							</div>
						))}
					</div>
				) : (
					<div className="text-center py-8 h-full flex flex-col items-center justify-center">
						<BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-4" />
						<h4 className="font-semibold text-gray-800">Citations Panel</h4>
						<p className="text-gray-500 text-sm mt-2 max-w-xs mx-auto">
							Sources used to generate responses will appear here as you chat.
						</p>
					</div>
				)}
			</div>
		</div>
	);

	// --- MAIN RENDER ---
	return (
		<div className="h-screen w-screen bg-gray-50 flex flex-col font-sans">
			<header className="bg-white border-b border-gray-200 px-4 sm:px-6 py-3 z-20 flex-shrink-0">
				<div className="w-full mx-auto flex items-center justify-between">
					<div className="flex items-center gap-3">
						<div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
							<Brain className="w-6 h-6 text-white" />
						</div>
						<div>
							<h1 className="text-lg sm:text-xl font-bold text-gray-900">ConvoTrack</h1>
							<p className="text-xs sm:text-sm text-gray-500">Autonomous BI Agent</p>
						</div>
					</div>
					<div className="flex items-center gap-4">
						<StatusIndicator status={apiStatus} />
						<button
							onClick={() => setIsSidebarOpen(!isSidebarOpen)}
							className="p-2 hover:bg-gray-100 rounded-lg lg:hidden"
						>
							<Menu className="w-5 h-5 text-gray-600" />
						</button>
					</div>
				</div>
			</header>

			<div className="flex-1 flex overflow-hidden">
				<main className="flex-1 flex flex-col">
					<div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6">
						<div className="max-w-4xl w-full mx-auto">
							{messages.length === 0 ? (
								<div className="flex flex-col items-center justify-center h-full text-center">
									<motion.div
										initial={{ scale: 0 }}
										animate={{ scale: 1 }}
										transition={{ duration: 0.5 }}
										className="p-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mb-6"
									>
										<MessageCircle className="w-12 h-12 text-white" />
									</motion.div>
									<h2 className="text-2xl font-bold text-gray-900 mb-3">Welcome to ConvoTrack</h2>
									<p className="text-gray-600 mb-8 max-w-md">
										Ask me anything about business intelligence, market trends, or consumer behavior.
									</p>
								</div>
							) : (
								<div className="space-y-8">
									{messages.map((message) => (
										<motion.div
											key={message.id}
											initial={{ opacity: 0, y: 20 }}
											animate={{ opacity: 1, y: 0 }}
											className={`w-full flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
										>
											<div
												className={`flex items-start gap-3 max-w-2xl ${
													message.type === "user" ? "flex-row-reverse" : "flex-row"
												}`}
											>
												<div
													className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
														message.type === "user" ? "bg-gray-200" : "bg-gradient-to-r from-blue-500 to-purple-600"
													}`}
												>
													{message.type === "user" ? (
														<User className="w-4 h-4 text-gray-600" />
													) : (
														<Brain className="w-4 h-4 text-white" />
													)}
												</div>

												<div className={`flex flex-col ${message.type === "user" ? "items-end" : "items-start"}`}>
													<div
														className={`w-full rounded-2xl p-4 shadow-sm ${
															message.type === "user"
																? "bg-gradient-to-r from-blue-500 to-purple-600 text-white"
																: message.type === "error"
																? "bg-red-50 border border-red-200 text-red-800"
																: "bg-white border border-gray-200 text-gray-900"
														}`}
													>
														{message.type === "bot" && message.analysisType && (
															<div
																className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium mb-3 ${message.analysisType.lightColor}`}
															>
																<message.analysisType.icon className="w-3 h-3" />
																AI Chose: {message.analysisType.name}
															</div>
														)}
														<ReactMarkdown className="prose prose-sm max-w-none text-left">
															{message.content}
														</ReactMarkdown>
													</div>

													<div className="text-xs text-gray-400 mt-1.5 px-2">
														{message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
													</div>
												</div>
											</div>
										</motion.div>
									))}
									{isLoading && (
										<motion.div
											initial={{ opacity: 0, y: 20 }}
											animate={{ opacity: 1, y: 0 }}
											className="w-full flex justify-start"
										>
											<div className="flex items-start gap-3 max-w-2xl">
												<div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gradient-to-r from-blue-500 to-purple-600">
													<Brain className="w-4 h-4 text-white" />
												</div>
												<div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-sm">
													<div className="flex items-center gap-3">
														<Loader className="w-4 h-4 animate-spin text-blue-500" />
														<span className="text-gray-600">Multi-agent system is thinking...</span>
													</div>
												</div>
											</div>
										</motion.div>
									)}
								</div>
							)}
							<div ref={messagesEndRef} />
						</div>
					</div>

					<div className="border-t border-gray-200 bg-white px-4 sm:px-6 py-4">
						<div className="max-w-4xl mx-auto">
							<form
								onSubmit={handleInputSubmit}
								className="flex gap-3"
							>
								<input
									type="text"
									value={inputValue}
									onChange={(e) => setInputValue(e.target.value)}
									placeholder="Ask an intelligent business question..."
									className="flex-1 px-4 py-3 border border-gray-300 bg-gray-50 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
									disabled={isLoading}
								/>
								<motion.button
									type="submit"
									disabled={isLoading || !inputValue.trim()}
									className="px-5 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium disabled:opacity-50"
									whileHover={{ scale: 1.03 }}
									whileTap={{ scale: 0.98 }}
								>
									<Send className="w-4 h-4" />
								</motion.button>
							</form>
						</div>
					</div>
				</main>

				{/* Desktop Sidebar (Right) */}
				<aside className="w-96 bg-white border-l border-gray-200 hidden lg:flex flex-col flex-shrink-0">
					<Sidebar />
				</aside>
			</div>

			{/* Mobile Sidebar (Overlay from Right) */}
			<AnimatePresence>
				{isSidebarOpen && (
					<motion.div
						className="fixed inset-0 z-30 lg:hidden"
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						exit={{ opacity: 0 }}
					>
						<div
							className="absolute inset-0 bg-black/40"
							onClick={() => setIsSidebarOpen(false)}
						></div>
						<motion.div
							className="absolute top-0 right-0 h-full w-full max-w-xs bg-white shadow-xl"
							initial={{ x: "100%" }}
							animate={{ x: "0%" }}
							exit={{ x: "100%" }}
							transition={{ type: "spring", stiffness: 300, damping: 30 }}
						>
							<Sidebar />
						</motion.div>
					</motion.div>
				)}
			</AnimatePresence>
		</div>
	);
}

export default App;
