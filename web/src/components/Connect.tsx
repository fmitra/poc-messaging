import { h, Component } from 'preact';

import authorize from '@messaging/api/authorize';
import connect from '@messaging/api/connect';

interface State {
  username: string;
  isAuthorized: boolean;
  errorMessage: string;
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

    this.setState({ isAuthorized: true });
    connect(token, this.props.onMessage, null);
  }

  handleUsername = (e: Event): void => {
    const { value } = (e.currentTarget as HTMLFormElement);
    this.setState({ username: value });
  }

  render(): JSX.Element {
    const NotAuthorized = (
      <form class='authorize'>
        <input
          type='text'
          class='authorize__input'
          value={this.state.username}
          onChange={this.handleUsername}
        />
        <button class='authorize__btn' onClick={this.handleConnect}>
          Authorize
        </button>
        {
          this.state.errorMessage &&
          <div class='authorize__error'>
            Please try again: {this.state.errorMessage}
          </div>
        }
      </form>
    );

    if (!this.state.isAuthorized) {
      return NotAuthorized;
    } else {
      return <div>Connected...</div>
    }
  }
};
