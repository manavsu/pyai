import { BASE_URL } from './config';

export async function create_new_agent() {
	try {
		const response = await fetch(`${BASE_URL}/new_agent/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			credentials: 'include'
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
	} catch (error) {
		console.error(error);
	}
}

export async function query_agent(input: string) {
	try {
		const response = await fetch(`${BASE_URL}/query/`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			credentials: 'include',
			body: JSON.stringify({ input })
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

export async function get_file(filename: string) {
    try {
        console.log('Fetching file:', filename);
        const response = await fetch(`${BASE_URL}/get_file/${filename}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
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
    }
}

function parse_notifications(notifications: any) {
    notifications.forEach((notification: any) => {
        console.log('Notification:', notification);
    });
}