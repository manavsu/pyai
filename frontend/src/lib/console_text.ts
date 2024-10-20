export enum MessageType {
	Text = 'text',
	Code = 'code'
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
