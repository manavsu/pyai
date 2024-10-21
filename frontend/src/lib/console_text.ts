export enum MessageType {
	Text = 'text',
    Code = 'code',
	Markdown = 'md',
    File = 'file'
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
}

export enum NotificationType {
    File = 'file',
    ToolCall = 'tool_call'
}

export interface Notification {
    type: NotificationType;
    content: string;
}
