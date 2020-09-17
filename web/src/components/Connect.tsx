import { h, Component } from 'preact';

import authorize from '@messaging/api/authorize';
import connect from '@messaging/api/connect';

interface State {
  username: string;
  isAuthorized: boolean;
  errorMessage: string;
  socket: WebSocket | null;
}

interface Props {
  onMessage: { (message: string): void };
}

export default class Connect extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      username: '',
      isAuthorized: false,
      errorMessage: '',
      socket: null,
    };
  }

  static defaultProps = {
    onMessage: (m: string): void => {},
  }

  handleConnect = async (e: Event): Promise<void> => {
    e.preventDefault();

    let token: string;

    try {
      token = await authorize(this.state.username);
    } catch (e) {
      this.setState({ errorMessage: e.message });
      return;
    }

    const ws = connect(token, this.props.onMessage, null);
    this.setState({
      isAuthorized: true,
      socket: ws,
    });
  }

  handleUsername = (e: Event): void => {
    const { value } = (e.currentTarget as HTMLFormElement);
    this.setState({ username: value });
  }

  handleDisconnect = (e: Event): void => {
    e.preventDefault();
    if (this.state.socket) {
      this.state.socket.close();
    }
  }

  render(): JSX.Element {
    const NotAuthorized = (
      <form class='connect__connect'>
        <input
          type='text'
          value={this.state.username}
          onChange={this.handleUsername}
        />
        <button onClick={this.handleConnect}>
          Authorize
        </button>
        {
          this.state.errorMessage &&
          <div class='connect__error'>
            Please try again: {this.state.errorMessage}
          </div>
        }
      </form>
    );

    const Disconnect = (
      <button class='connect__disconnect' onClick={this.handleDisconnect}>
        Disconnect
      </button>
    );

    if (!this.state.isAuthorized) {
      return NotAuthorized;
    } else {
      return Disconnect;
    }
  }
};
