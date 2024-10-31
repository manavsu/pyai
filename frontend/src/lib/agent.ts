import { BASE_URL } from './config';

export async function create_new_agent() {
	try {
		const response = await fetch(`${BASE_URL}/new_agent/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
		});

		if (!response.ok) {
			if (response.status != 400) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const errorData = await response.json();
			console.log(errorData.error);
			return;
		}

		const data = await response.json();
		console.log(data.message);
		return data.agent_id;
	} catch (error) {
		console.error(error);
	}
}

export async function query_agent(agent_id: string, input: string, attachments: {file:string, url:string}[] = []) {
	try {
		console.log('Querying agent with input:', input, attachments);
		const formData = new FormData();
		formData.append('query', input);
		formData.append('agent_id', agent_id)

        for (const attachment of attachments) {
            const response = await fetch(attachment.url);
            const blob = await response.blob();
            formData.append('attachments', blob, attachment.file);
        }

		const response = await fetch(`${BASE_URL}/query/`, {
			method: 'POST',
			headers: {'accept': 'application/json'},
			body: formData
		});

		if (!response.ok) {
			if (response.status != 400) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const errorData = await response.json();
			console.log(errorData.error);
			return;
		}

		const data = await response.json();
		const message = data.message;
		const notifications = data.notifications;

		console.log('Message from server:', message);
		console.log('Notifications:', notifications);
		return { message: message, notifications: notifications };
	} catch (error) {
		console.error('Error querying agent:', error);
	}
}

export async function get_file(agent_id: string, filename: string) {
    try {
        console.log('Fetching file:', filename);
        const response = await fetch(`${BASE_URL}/get_file/${agent_id}/${filename}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const fileBlob = await response.blob();
        const fileURL = URL.createObjectURL(fileBlob);

        console.log('File URL:', fileURL);
        if (!fileURL) console.error('File URL is empty');
        return fileURL;
    } catch (error) {
        console.error('Error fetching file:', error);
		return null
    }
}

function parse_notifications(notifications: any) {
    notifications.forEach((notification: any) => {
        console.log('Notification:', notification);
    });
}