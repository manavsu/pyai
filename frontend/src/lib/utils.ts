import { type Notification, NotificationType, MessageType} from '$lib/console_text';

export function getFileType(fileName: string) {
    const extension = fileName.split('.').pop()!.toLowerCase();
    console.log(extension);
    if (['png', 'jpg', 'jpeg', 'gif'].includes(extension)) return MessageType.Image;
    if (['csv', 'txt', 'md', 'json', 'xml', 'log', 'html'].includes(extension)) return MessageType.File;
    return MessageType.File;
  }

export function replaceSandboxCall(text: string, file_to_url: {file:string, url:string}[]) {
    return text.replace(/\(sandbox:\/(.*?)\)/g, (match, p1) => {
        const filename = p1.trim();
        const url = file_to_url.find(entry => entry.file === filename);
        return `(${url})`;
    });
}