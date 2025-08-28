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
	User, // Added for user avatar
	ChevronDown, // Added for accordion
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import axios from "axios";

// It's better practice to use environment variables for API URLs
// For this example, we'll use a placeholder.
const API_BASE_URL = "http://localhost:8000"; // Replace with your actual API endpoint

function App() {
	// State management
	const [messages, setMessages] = useState([]);
	const [inputValue, setInputValue] = useState("");
	const [isLoading, setIsLoading] = useState(false);
	const [showAnalysisOptions, setShowAnalysisOptions] = useState(false);
	const [apiStatus, setApiStatus] = useState("checking");
	const [selectedMessageSources, setSelectedMessageSources] = useState([]);
	const [isSidebarOpen, setIsSidebarOpen] = useState(false); // State for mobile sidebar
	const [expandedSourceIndex, setExpandedSourceIndex] = useState(null); // For citation accordion

	const messagesEndRef = useRef(null);

	// Analysis types configuration
	const analysisTypes = [
		{
			id: "strategic",
			name: "Strategic Analysis",
			description: "Long-term planning and positioning insights",
			icon: Target,
			color: "from-blue-500 to-blue-600",
			lightColor: "bg-blue-50 text-blue-700",
		},
		{
			id: "trends",
			name: "Trend Analysis",
			description: "Market trends and future outlook analysis",
			icon: TrendingUp,
			color: "from-green-500 to-green-600",
			lightColor: "bg-green-50 text-green-700",
		},
		{
			id: "comparative",
			name: "Comparative Analysis",
			description: "Side-by-side comparison with benchmarks",
			icon: BarChart3,
			color: "from-purple-500 to-purple-600",
			lightColor: "bg-purple-50 text-purple-700",
		},
		{
			id: "executive",
			name: "Executive Summary",
			description: "C-level decision making insights",
			icon: FileText,
			color: "from-orange-500 to-orange-600",
			lightColor: "bg-orange-50 text-orange-700",
		},
	];

	// Effect to scroll to the latest message
	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	};

	useEffect(() => {
		scrollToBottom();
	}, [messages, isLoading]);

	// Effect to check API health on component mount
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

	// Handler for submitting the input form
	const handleInputSubmit = (e) => {
		e.preventDefault();
		if (!inputValue.trim()) return;
		setShowAnalysisOptions(true);
	};

	// Handler for selecting an analysis type and sending the request
	const handleAnalysisTypeSelect = async (analysisType) => {
		if (!inputValue.trim()) return;

		const userMessage = {
			id: Date.now(),
			type: "user",
			content: inputValue,
			analysisType: analysisType,
			timestamp: new Date(),
		};

		setMessages((prev) => [...prev, userMessage]);
		const currentInput = inputValue;
		setInputValue("");
		setShowAnalysisOptions(false);
		setIsLoading(true);

		try {
			const response = await axios.post(`${API_BASE_URL}/ask`, {
				question: currentInput,
				analysis_type: analysisType.id,
			});

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

			if (responseSources.length > 0) {
				setSelectedMessageSources(responseSources);
				setExpandedSourceIndex(null); // Reset accordion on new message
				if (window.innerWidth < 1024) {
					setIsSidebarOpen(true);
				}
			}
		} catch (error) {
			console.error("Failed to get response:", error);
			const errorMessage = {
				id: Date.now() + 1,
				type: "error",
				content: "Sorry, I encountered an error. Please check the connection or try again.",
				timestamp: new Date(),
			};
			setMessages((prev) => [...prev, errorMessage]);
		} finally {
			setIsLoading(false);
		}
	};

	// Component to display API connection status
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

	// Component for the sidebar with sources
	const Sidebar = () => (
		<div className="h-full w-full bg-white border-l border-gray-200 flex flex-col">
			<div className="p-4 sm:p-6 border-b flex items-center justify-between flex-shrink-0">
				<div className="flex items-center gap-2">
					<BookOpen className="w-5 h-5 text-gray-600" />
					<h3 className="font-semibold text-gray-900">Sources & Citations</h3>
				</div>
				<button
					onClick={() => setIsSidebarOpen(false)}
					className="p-1 hover:bg-gray-100 rounded-lg lg:hidden"
				>
					<X className="w-5 h-5 text-gray-500" />
				</button>
			</div>
			<div className="flex-1 overflow-y-auto p-4 sm:p-6">
				{selectedMessageSources.length > 0 ? (
					<div className="space-y-3">
						{selectedMessageSources.map((source, index) => (
							<div
								key={index}
								className="bg-gray-50 rounded-lg border border-gray-200 overflow-hidden"
							>
								<button
									onClick={() => setExpandedSourceIndex(expandedSourceIndex === index ? null : index)}
									className="w-full p-3 text-left flex items-center justify-between hover:bg-gray-100 transition-colors"
								>
									<div className="flex-1">
										<p className="text-sm font-medium text-blue-600">Source {index + 1}</p>
										<p className="text-xs text-gray-500 break-all mt-1">{source.url}</p>
									</div>
									<ChevronDown
										className={`w-5 h-5 text-gray-500 transition-transform ${expandedSourceIndex === index ? "rotate-180" : ""}`}
									/>
								</button>
								<AnimatePresence>
									{expandedSourceIndex === index && (
										<motion.div
											initial={{ height: 0, opacity: 0 }}
											animate={{ height: "auto", opacity: 1 }}
											exit={{ height: 0, opacity: 0 }}
											transition={{ duration: 0.3 }}
											className="overflow-hidden"
										>
											<div className="p-3 border-t border-gray-200 text-sm text-gray-700 bg-white">
												<p className="font-semibold mb-2">Extracted Content:</p>
												<pre className="text-xs whitespace-pre-wrap font-sans bg-gray-100 p-2 rounded-md max-h-48 overflow-y-auto">
													{source.content}
												</pre>
												<a
													href={source.url}
													target="_blank"
													rel="noopener noreferrer"
													className="p-1 mt-2 inline-flex items-center gap-1.5 text-blue-600 hover:underline"
													title="Open source"
												>
													<ExternalLink className="w-3 h-3" />
													Visit Link
												</a>
											</div>
										</motion.div>
									)}
								</AnimatePresence>
							</div>
						))}
					</div>
				) : (
					<div className="text-center py-8 h-full flex flex-col items-center justify-center">
						<BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-3" />
						<p className="text-gray-500 text-sm">Sources will appear here when you receive responses with citations.</p>
					</div>
				)}
			</div>
		</div>
	);

	return (
		<div className="h-screen w-screen bg-gray-50 flex flex-col font-sans">
			{/* Header */}
			<header className="bg-white border-b border-gray-200 px-4 sm:px-6 py-3 z-20 flex-shrink-0">
				<div className="w-full mx-auto flex items-center justify-between">
					<div className="flex items-center gap-3">
						<div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
							<Brain className="w-6 h-6 text-white" />
						</div>
						<div>
							<h1 className="text-lg sm:text-xl font-bold text-gray-900">ConvoTrack</h1>
							<p className="text-xs sm:text-sm text-gray-500">AI Business Intelligence</p>
						</div>
					</div>
					<div className="flex items-center gap-4">
						<StatusIndicator status={apiStatus} />
						<button
							onClick={() => setIsSidebarOpen(true)}
							className="p-2 hover:bg-gray-100 rounded-lg lg:hidden"
						>
							<Menu className="w-5 h-5 text-gray-600" />
						</button>
					</div>
				</div>
			</header>

			{/* Main Content */}
			<div className="flex-1 flex overflow-hidden">
				{/* Main Chat Area */}
				<main className="flex-1 flex flex-col">
					{/* Messages Area */}
					<div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6">
						<div className="max-w-4xl mx-auto">
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
									<div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
										{[
											"What are the latest marketing trends?",
											"Analyze consumer behavior patterns",
											"Compare platform performance",
											"Strategic growth opportunities",
										].map((prompt) => (
											<motion.button
												key={prompt}
												onClick={() => setInputValue(prompt)}
												className="p-3 bg-white border border-gray-200 rounded-lg text-sm text-gray-700 hover:border-gray-300 hover:shadow-sm transition-all duration-200"
												whileHover={{ scale: 1.02 }}
												whileTap={{ scale: 0.98 }}
											>
												{prompt}
											</motion.button>
										))}
									</div>
								</div>
							) : (
								<div className="space-y-6">
									{messages.map((message) => (
										<motion.div
											key={message.id}
											initial={{ opacity: 0, y: 20 }}
											animate={{ opacity: 1, y: 0 }}
											transition={{ duration: 0.3 }}
											className={`flex items-start gap-3 ${message.type === "user" ? "justify-end" : "justify-start"}`}
										>
											{/* Avatar */}
											<div
												className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
													message.type === "user" ? "bg-gray-200" : "bg-gradient-to-r from-blue-500 to-purple-600"
												} ${message.type === "user" ? "order-2" : "order-1"}`}
											>
												{message.type === "user" ? (
													<User className="w-4 h-4 text-gray-600" />
												) : (
													<Brain className="w-4 h-4 text-white" />
												)}
											</div>

											{/* Message Bubble & Timestamp */}
											<div className={`flex flex-col ${message.type === "user" ? "order-1 items-end" : "order-2 items-start"}`}>
												<div
													className={`max-w-full ${
														message.type === "user"
															? "bg-gradient-to-r from-blue-500 to-purple-600 text-white"
															: message.type === "error"
															? "bg-red-50 border border-red-200 text-red-800"
															: "bg-white border border-gray-200 text-gray-900"
													} rounded-2xl p-4 shadow-sm`}
													onClick={() => {
														if (message.type === "bot" && message.sources) {
															setSelectedMessageSources(message.sources);
															setIsSidebarOpen(true);
														}
													}}
												>
													{message.type === "user" ? (
														<div>
															<p className="font-medium">{message.content}</p>
															{message.analysisType && (
																<div className="mt-2 flex items-center gap-2">
																	<message.analysisType.icon className="w-4 h-4 opacity-80" />
																	<span className="text-sm opacity-80">{message.analysisType.name}</span>
																</div>
															)}
														</div>
													) : (
														<div>
															{message.analysisType && (
																<div
																	className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium mb-3 ${message.analysisType.lightColor}`}
																>
																	<message.analysisType.icon className="w-3 h-3" />
																	{message.analysisType.name}
																</div>
															)}
															<ReactMarkdown
																className="prose prose-sm max-w-none"
																components={{
																	p: ({ children }) => (
																		<p className="mb-3 last:mb-0 leading-relaxed text-gray-700">{children}</p>
																	),
																	ul: ({ children }) => (
																		<ul className="list-disc pl-5 mb-3 space-y-1 text-gray-700">{children}</ul>
																	),
																	ol: ({ children }) => (
																		<ol className="list-decimal pl-5 mb-3 space-y-1 text-gray-700">{children}</ol>
																	),
																	strong: ({ children }) => (
																		<strong className="font-semibold text-gray-900">{children}</strong>
																	),
																	h1: ({ children }) => (
																		<h1 className="text-lg font-bold mb-2 text-gray-900">{children}</h1>
																	),
																}}
															>
																{message.content}
															</ReactMarkdown>
															{message.confidence && (
																<div className="mt-3 pt-3 border-t border-gray-100">
																	<div className="flex items-center justify-between text-xs">
																		<span className="text-gray-500">
																			Confidence: {message.confidence.toUpperCase()}
																		</span>
																		{message.sources && message.sources.length > 0 && (
																			<button
																				onClick={(e) => {
																					e.stopPropagation();
																					setSelectedMessageSources(message.sources);
																					setIsSidebarOpen(true);
																				}}
																				className="flex items-center gap-1 text-blue-600 hover:text-blue-800 transition-colors"
																			>
																				<BookOpen className="w-3 h-3" />
																				<span>{message.sources.length} sources</span>
																			</button>
																		)}
																	</div>
																</div>
															)}
														</div>
													)}
												</div>
												<div className="text-xs text-gray-400 mt-1.5 px-2">
													{message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
												</div>
											</div>
										</motion.div>
									))}
									{isLoading && (
										<motion.div
											initial={{ opacity: 0, y: 20 }}
											animate={{ opacity: 1, y: 0 }}
											className="flex items-start gap-3 justify-start"
										>
											<div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gradient-to-r from-blue-500 to-purple-600">
												<Brain className="w-4 h-4 text-white" />
											</div>
											<div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-sm">
												<div className="flex items-center gap-3">
													<Loader className="w-4 h-4 animate-spin text-blue-500" />
													<span className="text-gray-600">Analyzing your question...</span>
												</div>
											</div>
										</motion.div>
									)}
								</div>
							)}
							<div ref={messagesEndRef} />
						</div>
					</div>

					{/* Input Area */}
					<div className="border-t border-gray-200 bg-white px-4 sm:px-6 py-4 flex-shrink-0">
						<div className="max-w-4xl mx-auto">
							<form
								onSubmit={handleInputSubmit}
								className="flex gap-3"
							>
								<input
									type="text"
									value={inputValue}
									onChange={(e) => setInputValue(e.target.value)}
									placeholder="Ask a question about business intelligence..."
									className="flex-1 px-4 py-3 border border-gray-300 bg-gray-50 text-black rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
									disabled={isLoading}
									autoComplete="off"
								/>
								<motion.button
									type="submit"
									disabled={isLoading || !inputValue.trim()}
									className="px-5 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-md hover:shadow-lg transition-shadow"
									whileHover={{ scale: 1.03 }}
									whileTap={{ scale: 0.98 }}
								>
									<Send className="w-4 h-4" />
									<span className="hidden sm:inline">Send</span>
								</motion.button>
							</form>
						</div>
					</div>
				</main>

				{/* Desktop Sidebar */}
				<aside className="w-96 bg-white border-l border-gray-200 hidden lg:flex flex-col flex-shrink-0">
					<Sidebar />
				</aside>

				{/* Mobile Sidebar */}
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

			{/* Analysis Type Selection Modal */}
			<AnimatePresence>
				{showAnalysisOptions && (
					<motion.div
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						exit={{ opacity: 0 }}
						className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center p-4 z-50"
						onClick={() => setShowAnalysisOptions(false)}
					>
						<motion.div
							initial={{ scale: 0.9, opacity: 0 }}
							animate={{ scale: 1, opacity: 1 }}
							exit={{ scale: 0.9, opacity: 0 }}
							className="bg-white rounded-2xl p-6 max-w-lg w-full shadow-xl"
							onClick={(e) => e.stopPropagation()}
						>
							<div className="flex items-center justify-between mb-4">
								<h3 className="text-lg font-bold text-gray-900">Choose Analysis Type</h3>
								<button
									onClick={() => setShowAnalysisOptions(false)}
									className="p-1 hover:bg-gray-100 rounded-lg"
								>
									<X className="w-5 h-5 text-gray-500" />
								</button>
							</div>
							<p className="text-gray-600 mb-6 text-sm">
								Select the type of analysis for: <span className="font-medium text-gray-800">"{inputValue}"</span>
							</p>
							<div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
								{analysisTypes.map((type) => (
									<motion.button
										key={type.id}
										onClick={() => handleAnalysisTypeSelect(type)}
										className="p-4 border border-gray-200 rounded-xl text-left hover:border-blue-400 hover:shadow-md transition-all duration-200 group"
										whileHover={{ scale: 1.02 }}
										whileTap={{ scale: 0.98 }}
									>
										<div className="flex items-start gap-4">
											<div className={`p-2 bg-gradient-to-r ${type.color} rounded-lg mt-1`}>
												<type.icon className="w-5 h-5 text-white" />
											</div>
											<div className="flex-1">
												<h4 className="font-semibold text-gray-900 group-hover:text-blue-600">{type.name}</h4>
												<p className="text-sm text-gray-600 mt-1">{type.description}</p>
											</div>
										</div>
									</motion.button>
								))}
							</div>
						</motion.div>
					</motion.div>
				)}
			</AnimatePresence>
		</div>
	);
}

export default App;
