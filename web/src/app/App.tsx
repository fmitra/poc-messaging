import { h, Component } from 'preact';

import Connect from '@messaging/components/Connect';
import Notifications from '@messaging/components/Notifications';

interface State {
  messages: string[];
}

export default class App extends Component<{}, State> {
  constructor(props: {}) {
    super(props);
    this.state = { messages: [] };
  }

  onMessage = (message: string): void => {
    const messages = this.state.messages
    messages.push(message);
    this.setState({ messages });
  }

  render(): JSX.Element {
    return (
      <div class='app'>
        <Connect onMessage={this.onMessage} />
        <Notifications notifications={this.state.messages} />
      </div>
    );
  }
};
