export enum MessageType {
	Text = 'text',
    Code = 'code',
	Markdown = 'md',
    File = 'file',
    URL = 'url',
    Image = 'image',
    TextFile = 'text_file',
    Loading = 'loading',
}

export enum Origin {
    System = 'system',
    User = 'user',
    Agent = 'agent'
}

export interface ConsoleMessage {
	type: MessageType;
    origin: Origin;
	content: string;
    attachments?: string[];
}

export enum NotificationType {
    File = 'file',
    ToolCall = 'tool_call'
}

export interface Notification {
    type: NotificationType;
    content: string;
}
